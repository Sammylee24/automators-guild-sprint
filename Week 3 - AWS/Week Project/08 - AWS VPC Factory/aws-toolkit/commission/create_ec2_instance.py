# create_ec2_instance.py
import boto3
import argparse

def _get_latest_amazon_linux_ami(ec2_client):
    response = ec2_client.describe_images(
        Owners=['amazon'],
        Filters=[
            {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
            {'Name': 'state', 'Values': ['available']},
        ]
    )
    images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
    return images[0]['ImageId']

def create_ec2_instance(ec2_client, name, subnet_id, key_name, sg_id, is_public=False):
    print(f"Creating EC2 Instance '{name}'...")
    try:
        ami_id = _get_latest_amazon_linux_ami(ec2_client)
        print(f"   - Using latest Amazon Linux 2 AMI: {ami_id}")

        instance_response = ec2_client.run_instances(
            ImageId=ami_id,
            InstanceType='t2.micro',
            KeyName=key_name,
            MaxCount=1,
            MinCount=1,
            NetworkInterfaces=[{
                'DeviceIndex': 0,
                'SubnetId': subnet_id,
                'Groups': [sg_id],
                'AssociatePublicIpAddress': is_public
            }],
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': name}]
            }]
        )
        instance_id = instance_response['Instances'][0]['InstanceId']
        print(f"✅ Instance '{name}' launched with ID: {instance_id}")

        print("     - Waiting for instance to enter 'running' state...")
        waiter = ec2_client.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        print("✅ Instance is now running.")
        
        # If public, get and display the public IP
        if is_public:
            desc = ec2_client.describe_instances(InstanceIds=[instance_id])
            public_ip = desc['Reservations'][0]['Instances'][0].get('PublicIpAddress', 'N/A')
            print(f"   - Public IP: {public_ip}")
            print(f"\n🌐 SSH command: ssh -i '{key_name}.pem' ec2-user@{public_ip}")

        return instance_id

    except Exception as e:
        print(f"❌ Error creating EC2 instance: {e}")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Launch an EC2 instance.")
    parser.add_argument('--name', required=True, help='Name tag for the instance.')
    parser.add_argument('--subnet-id', required=True, help='Subnet ID to launch the instance in.')
    parser.add_argument('--key-name', required=True, help='Name of the EC2 key pair to use.')
    parser.add_argument('--sg-id', required=True, help='Security Group ID to attach.')
    parser.add_argument('--public', action='store_true', help='Assign a public IP address (use for public subnets).')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    create_ec2_instance(client, args.name, args.subnet_id, args.key_name, args.sg_id, args.public)
    
# create_vpc.py
import boto3
import argparse

def create_vpc(ec2_client, cidr, name):
    print(f"Creating VPC '{name}' with CIDR {cidr}...")
    vpc_response = ec2_client.create_vpc(CidrBlock=cidr)
    vpc_id = vpc_response['Vpc']['VpcId']
    
    ec2_client.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name', 'Value': name}])
    
    waiter = ec2_client.get_waiter('vpc_available')
    waiter.wait(VpcIds=[vpc_id])
    
    print(f"✅ VPC '{name}' created successfully.")
    print(f"   - VPC ID: {vpc_id}")
    return vpc_id

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create an AWS VPC.")
    parser.add_argument('--cidr', type=str, required=True, help='The CIDR block for the VPC (e.g., 10.0.0.0/16)')
    parser.add_argument('--name', type=str, required=True, help='The name tag for the VPC (e.g., My-VPC)')
    args = parser.parse_args()

    client = boto3.client('ec2')
    create_vpc(client, args.cidr, args.name)
    
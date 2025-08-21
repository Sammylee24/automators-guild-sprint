# terminate_instances.py
import boto3
import argparse

def terminate_instances_in_vpc(ec2_client, vpc_id):
    try:
        reservations = ec2_client.describe_instances(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Reservations']
        instance_ids = [inst['InstanceId'] for res in reservations for inst in res['Instances']]

        if not instance_ids:
            print(f"✅ No EC2 instances found in VPC {vpc_id}.")
            return

        print(f"Terminating {len(instance_ids)} instance(s)...")
        ec2_client.terminate_instances(InstanceIds=instance_ids)
        waiter = ec2_client.get_waiter('instance_terminated')
        waiter.wait(InstanceIds=instance_ids)
        print("✅ All EC2 instances terminated successfully.")
    except Exception as e:
        print(f"❌ Error terminating instances: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Terminate all EC2 instances within a specified VPC.")
    parser.add_argument('--vpc-id', required=True, help='The ID of the VPC whose instances you want to terminate.')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    terminate_instances_in_vpc(client, args.vpc_id)
    
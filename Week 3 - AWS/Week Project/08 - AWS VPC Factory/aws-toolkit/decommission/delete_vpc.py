# delete_vpc.py
import boto3
import argparse

def delete_vpc(ec2_client, vpc_id):
    try:
        print(f"🗑️ Deleting VPC {vpc_id}...")
        ec2_client.delete_vpc(VpcId=vpc_id)
        print(f"✅ VPC {vpc_id} has been deleted.")
    except Exception as e:
        print(f"❌ Error deleting VPC. Ensure all dependencies (subnets, gateways, etc.) are removed first. Error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Delete a VPC.")
    parser.add_argument('--vpc-id', required=True, help='The ID of the VPC to delete.')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    delete_vpc(client, args.vpc_id)
    
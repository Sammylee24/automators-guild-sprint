# delete_subnets.py
import boto3
import argparse

def delete_subnets_in_vpc(ec2_client, vpc_id):
    try:
        subnets = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets']
        
        if not subnets:
            print(f"✅ No Subnets found in VPC {vpc_id}.")
            return

        print(f"Deleting {len(subnets)} Subnet(s)...")
        for subnet in subnets:
            subnet_id = subnet['SubnetId']
            print(f"   - Deleting Subnet {subnet_id}...")
            ec2_client.delete_subnet(SubnetId=subnet_id)
        
        print(f"✅ All subnets in VPC {vpc_id} have been deleted.")
    except Exception as e:
        print(f"❌ Error deleting Subnets: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Delete all Subnets within a specified VPC.")
    parser.add_argument('--vpc-id', required=True, help='The ID of the VPC.')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    delete_subnets_in_vpc(client, args.vpc_id)
    
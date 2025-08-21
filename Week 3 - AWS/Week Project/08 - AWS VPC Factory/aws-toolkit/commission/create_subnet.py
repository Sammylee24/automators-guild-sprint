# create_subnet.py
import boto3
import argparse

def create_subnet(ec2_client, vpc_id, cidr, name):
    print(f"Creating Subnet '{name}' in VPC {vpc_id} with CIDR {cidr}...")
    subnet_response = ec2_client.create_subnet(VpcId=vpc_id, CidrBlock=cidr)
    subnet_id = subnet_response['Subnet']['SubnetId']
    
    ec2_client.create_tags(Resources=[subnet_id], Tags=[{'Key': 'Name', 'Value': name}])
    
    print(f"✅ Subnet '{name}' created successfully.")
    print(f"   - Subnet ID: {subnet_id}")
    return subnet_id

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create an AWS Subnet in a specified VPC.")
    parser.add_argument('--vpc-id', type=str, required=True, help='The ID of the VPC to create the subnet in')
    parser.add_argument('--cidr', type=str, required=True, help='The CIDR block for the subnet (e.g., 10.0.1.0/24)')
    parser.add_argument('--name', type=str, required=True, help='The name tag for the subnet')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    create_subnet(client, args.vpc_id, args.cidr, args.name)
    
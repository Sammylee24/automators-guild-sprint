# create_igw.py
import boto3
import argparse

def create_and_attach_igw(ec2_client, vpc_id, name):
    print(f"Creating Internet Gateway '{name}'...")
    igw_response = ec2_client.create_internet_gateway()
    igw_id = igw_response['InternetGateway']['InternetGatewayId']
    ec2_client.create_tags(Resources=[igw_id], Tags=[{'Key': 'Name', 'Value': name}])
    print(f"✅ IGW created with ID: {igw_id}")
    
    print(f"   - Attaching IGW to VPC {vpc_id}...")
    ec2_client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    print("✅ IGW successfully attached.")
    return igw_id

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create and attach an Internet Gateway to a VPC.")
    parser.add_argument('--vpc-id', type=str, required=True, help='The ID of the VPC to attach the IGW to')
    parser.add_argument('--name', type=str, required=True, help='The name tag for the IGW')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    create_and_attach_igw(client, args.vpc_id, args.name)
    
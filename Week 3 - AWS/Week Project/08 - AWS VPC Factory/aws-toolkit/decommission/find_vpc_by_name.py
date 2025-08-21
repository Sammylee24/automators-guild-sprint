# find_vpc_by_name.py
import boto3
import argparse

def find_vpc_by_name(ec2_client, name):
    try:
        vpcs = ec2_client.describe_vpcs(Filters=[{'Name': 'tag:Name', 'Values': [name]}])['Vpcs']
        if not vpcs:
            print(f"No VPC found with the name '{name}'.")
            return None
        vpc_id = vpcs[0]['VpcId']
        print(f"Found VPC '{name}' with ID: {vpc_id}")
        return vpc_id
    except Exception as e:
        print(f"Error finding VPC: {e}")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find a VPC ID by its 'Name' tag.")
    parser.add_argument('--name', required=True, help='The Name tag of the VPC to find.')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    find_vpc_by_name(client, args.name)
    
# delete_igw.py
import boto3
import argparse

def delete_igw_in_vpc(ec2_client, vpc_id):
    try:
        igws = ec2_client.describe_internet_gateways(Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}])['InternetGateways']
        
        if not igws:
            print(f"✅ No Internet Gateway found in VPC {vpc_id}.")
            return

        for igw in igws:
            igw_id = igw['InternetGatewayId']
            print(f"Detaching IGW {igw_id}...")
            ec2_client.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
            print(f"Deleting IGW {igw_id}...")
            ec2_client.delete_internet_gateway(InternetGatewayId=igw_id)
        
        print(f"✅ Deleted {len(igws)} Internet Gateway(s).")
    except Exception as e:
        print(f"❌ Error deleting Internet Gateway: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Detach and delete the Internet Gateway from a VPC.")
    parser.add_argument('--vpc-id', required=True, help='The ID of the VPC.')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    delete_igw_in_vpc(client, args.vpc_id)
    
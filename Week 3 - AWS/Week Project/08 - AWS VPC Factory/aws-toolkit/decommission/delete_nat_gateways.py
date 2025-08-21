# delete_nat_gateways.py
import boto3
import argparse

def delete_nat_gateways_in_vpc(ec2_client, vpc_id):
    try:
        nat_gateways = ec2_client.describe_nat_gateways(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}, {'Name': 'state', 'Values': ['pending', 'available']}])['NatGateways']
        
        if not nat_gateways:
            print(f"✅ No active NAT Gateways found in VPC {vpc_id}.")
            return

        for nat_gw in nat_gateways:
            nat_gw_id = nat_gw['NatGatewayId']
            print(f"Deleting NAT Gateway {nat_gw_id}...")
            ec2_client.delete_nat_gateway(NatGatewayId=nat_gw_id)
            waiter = ec2_client.get_waiter('nat_gateway_deleted')
            print("   - Waiting for deletion to complete...")
            waiter.wait(NatGatewayIds=[nat_gw_id])
            print(f"✅ NAT Gateway {nat_gw_id} deleted.")
    except Exception as e:
        print(f"❌ Error deleting NAT Gateways: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Delete all NAT Gateways within a specified VPC.")
    parser.add_argument('--vpc-id', required=True, help='The ID of the VPC.')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    delete_nat_gateways_in_vpc(client, args.vpc_id)
    
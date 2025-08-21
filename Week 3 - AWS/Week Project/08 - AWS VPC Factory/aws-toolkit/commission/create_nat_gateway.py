# create_nat_gateway.py
import boto3
import argparse

def create_nat_gateway(ec2_client, subnet_id, name):
    print(f"Creating NAT Gateway '{name}'...")
    try:
        print("   - Allocating Elastic IP...")
        eip_response = ec2_client.allocate_address(Domain='vpc')
        eip_alloc_id = eip_response['AllocationId']
        print(f"     - EIP allocated with ID: {eip_alloc_id}")

        print(f"   - Creating NAT Gateway in Subnet {subnet_id}...")
        nat_gw_response = ec2_client.create_nat_gateway(
            SubnetId=subnet_id,
            AllocationId=eip_alloc_id
        )
        nat_gw_id = nat_gw_response['NatGateway']['NatGatewayId']
        ec2_client.create_tags(Resources=[nat_gw_id], Tags=[{'Key': 'Name', 'Value': name}])
        print(f"     - NAT Gateway created with ID: {nat_gw_id}")

        print("     - Waiting for NAT Gateway to become available...")
        waiter = ec2_client.get_waiter('nat_gateway_available')
        waiter.wait(NatGatewayIds=[nat_gw_id])
        
        print(f"✅ NAT Gateway '{name}' is now available.")
        print(f"   - NAT Gateway ID: {nat_gw_id}")
        return nat_gw_id

    except Exception as e:
        print(f"❌ Error creating NAT Gateway: {e}")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a NAT Gateway in a public subnet.")
    parser.add_argument('--subnet-id', required=True, help='The ID of the PUBLIC subnet to place the NAT Gateway in.')
    parser.add_argument('--name', required=True, help='The name tag for the NAT Gateway.')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    create_nat_gateway(client, args.subnet_id, args.name)
    
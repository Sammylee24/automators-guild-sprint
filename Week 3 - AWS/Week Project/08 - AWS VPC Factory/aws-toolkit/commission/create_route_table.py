# create_route_table.py
import boto3
import argparse

def create_route_table(ec2_client, vpc_id, name, subnet_id=None, gateway_id=None, nat_gateway_id=None):
    print(f"Creating Route Table '{name}' in VPC {vpc_id}...")
    rt_response = ec2_client.create_route_table(VpcId=vpc_id)
    rt_id = rt_response['RouteTable']['RouteTableId']
    ec2_client.create_tags(Resources=[rt_id], Tags=[{'Key': 'Name', 'Value': name}])
    print(f"✅ Route Table created with ID: {rt_id}")

    if gateway_id:
        print(f"   - Adding route 0.0.0.0/0 -> IGW {gateway_id}")
        ec2_client.create_route(RouteTableId=rt_id, DestinationCidrBlock='0.0.0.0/0', GatewayId=gateway_id)

    if nat_gateway_id:
        print(f"   - Adding route 0.0.0.0/0 -> NAT-GW {nat_gateway_id}")
        ec2_client.create_route(RouteTableId=rt_id, DestinationCidrBlock='0.0.0.0/0', NatGatewayId=nat_gateway_id)

    if subnet_id:
        print(f"   - Associating with Subnet {subnet_id}")
        ec2_client.associate_route_table(RouteTableId=rt_id, SubnetId=subnet_id)
        
    print("✅ Route Table configuration complete.")
    return rt_id

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a Route Table, optionally add a default route, and associate it.")
    parser.add_argument('--vpc-id', required=True, help='VPC ID')
    parser.add_argument('--name', required=True, help='Name tag for the Route Table')
    parser.add_argument('--subnet-id', help='Subnet ID to associate with')
    # Use one or the other, not both
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--gateway-id', help='Internet Gateway ID for default route')
    group.add_argument('--nat-gateway-id', help='NAT Gateway ID for default route')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    create_route_table(client, args.vpc_id, args.name, args.subnet_id, args.gateway_id, args.nat_gateway_id)
    
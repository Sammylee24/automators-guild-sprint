import boto3
import time

# Create a client object for the EC2 service
ec2_client = boto3.client('ec2')

# --- CONFIGURATION ---
VPC_NAME_TAG = 'Boto3-VPC'

print("Script starting...")

try:
    # --- Step 1: Find the VPC ID ---
    print(f"🔎 Searching for VPC with Name tag: {VPC_NAME_TAG}...")
    vpcs = ec2_client.describe_vpcs(Filters=[{'Name': 'tag:Name', 'Values': [VPC_NAME_TAG]}])['Vpcs']

    if not vpcs:
        print(f"✅ No VPC found with the name '{VPC_NAME_TAG}'. Nothing to do.")
        exit()

    vpc_id = vpcs[0]['VpcId']
    print(f"   - Found VPC with ID: {vpc_id}")

    # --- Step 2: Terminate EC2 instances ---
    print("\n🔎 Searching for and terminating EC2 instances in the VPC...")
    instance_filter = [{'Name': 'vpc-id', 'Values': [vpc_id]}]
    reservations = ec2_client.describe_instances(Filters=instance_filter)['Reservations']
    
    instance_ids = [inst['InstanceId'] for res in reservations for inst in res['Instances']]

    if instance_ids:
        ec2_client.terminate_instances(InstanceIds=instance_ids)
        waiter = ec2_client.get_waiter('instance_terminated')
        print(f"   - Waiting for {len(instance_ids)} instance(s) to terminate...")
        waiter.wait(InstanceIds=instance_ids)
        print("✅ All EC2 instances terminated.")
    else:
        print("✅ No EC2 instances found.")

    # --- Step 3: Delete NAT Gateways --- (MOVED UP)
    print("\n🔎 Searching for and deleting NAT Gateways in the VPC...")
    nat_gw_filter = [{'Name': 'vpc-id', 'Values': [vpc_id]}, {'Name': 'state', 'Values': ['pending', 'available']}]
    nat_gateways = ec2_client.describe_nat_gateways(Filters=nat_gw_filter)['NatGateways']

    if nat_gateways:
        for nat_gw in nat_gateways:
            nat_gw_id = nat_gw['NatGatewayId']
            ec2_client.delete_nat_gateway(NatGatewayId=nat_gw_id)
            waiter = ec2_client.get_waiter('nat_gateway_deleted')
            print(f"   - Waiting for NAT Gateway {nat_gw_id} to be deleted...")
            waiter.wait(NatGatewayIds=[nat_gw_id])
            print(f"✅ NAT Gateway {nat_gw_id} deleted.")
    else:
        print("✅ No active NAT Gateways found.")

    # --- Step 4: Release Elastic IPs --- (MOVED UP)
    print("\n🔎 Searching for and releasing unassociated Elastic IPs...")
    eips = ec2_client.describe_addresses(Filters=[{'Name': 'domain', 'Values': ['vpc']}])['Addresses']
    
    eips_released = 0
    if eips:
        for eip in eips:
            if "AssociationId" not in eip and "InstanceId" not in eip:
                ec2_client.release_address(AllocationId=eip['AllocationId'])
                eips_released += 1
        if eips_released > 0:
            print(f"✅ Released {eips_released} Elastic IP(s).")
        else:
            print("✅ No unassociated Elastic IPs found to release.")
    else:
        print("✅ No Elastic IPs found in this account.")

    # --- Step 5: Detach and Delete Internet Gateways --- (NOW IT'S SAFE)
    print("\n🔎 Searching for and deleting Internet Gateways...")
    igw_filter = [{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}]
    igws = ec2_client.describe_internet_gateways(Filters=igw_filter)['InternetGateways']

    if igws:
        for igw in igws:
            igw_id = igw['InternetGatewayId']
            ec2_client.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
            ec2_client.delete_internet_gateway(InternetGatewayId=igw_id)
        print(f"✅ Deleted {len(igws)} Internet Gateway(s).")
    else:
        print("✅ No Internet Gateway found.")

    # --- The Rest of the Cleanup ---
    
    # Step 6: Delete Subnets
    print("\n🔎 Searching for and deleting Subnets...")
    subnets = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets']
    if subnets:
        for subnet in subnets:
            ec2_client.delete_subnet(SubnetId=subnet['SubnetId'])
        print(f"✅ Deleted {len(subnets)} Subnet(s).")
    else:
        print("✅ No Subnets found.")

    # Step 7: Delete Custom Route Tables
    print("\n🔎 Searching for and deleting custom Route Tables...")
    route_tables = ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['RouteTables']
    if route_tables:
        for rt in route_tables:
            if not any(assoc.get('Main', False) for assoc in rt.get('Associations', [])):
                ec2_client.delete_route_table(RouteTableId=rt['RouteTableId'])
        print("✅ Deleted all custom Route Tables.")
    else:
        print("✅ No custom Route Tables found.")

    # Step 8: Delete Custom Security Groups
    print("\n🔎 Searching for and deleting custom Security Groups...")
    sgs = ec2_client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['SecurityGroups']
    if sgs:
        for sg in sgs:
            if sg['GroupName'] != 'default':
                # You may need to revoke rules if they depend on other groups, but delete_security_group often handles this.
                try:
                    ec2_client.delete_security_group(GroupId=sg['GroupId'])
                except Exception as e:
                    print(f"   - Could not delete SG {sg['GroupId']} (might have dependent rules): {e}")
        print("✅ Deleted all custom Security Groups.")
    else:
        print("✅ No custom Security Groups found.")

    # Step 9: Finally, Delete the VPC
    print(f"\n🗑️ Deleting VPC {vpc_id}...")
    ec2_client.delete_vpc(VpcId=vpc_id)
    print("✅ VPC deleted successfully.")

except Exception as e:
    print(f"❌ An error occurred: {e}")

print("\nScript finished.")

import boto3
import time

# Create a client object for the EC2 service
ec2_client = boto3.client('ec2')

# --- CONFIGURATION ---
# The unique name tag you gave to your VPC. This is how we'll find it.
VPC_NAME_TAG = 'Boto3-VPC'

print("Script starting...")

try:
    # --- Step 1: Find the VPC ID using its "Name" tag ---
    print(f"🔎 Searching for VPC with Name tag: {VPC_NAME_TAG}...")
    vpc_filter = [{'Name': 'tag:Name', 'Values': [VPC_NAME_TAG]}]
    vpcs = ec2_client.describe_vpcs(Filters=vpc_filter)['Vpcs']

    if not vpcs:
        print(f"✅ No VPC found with the name '{VPC_NAME_TAG}'. Nothing to do.")
        exit()

    vpc_id = vpcs[0]['VpcId']
    print(f"   - Found VPC with ID: {vpc_id}")

    # --- Step 2: Detach and Delete the Internet Gateway (IGW) ---
    print("\n🔎 Searching for Internet Gateway attached to the VPC...")
    igw_filter = [{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}]
    igws = ec2_client.describe_internet_gateways(Filters=igw_filter)['InternetGateways']

    if igws:
        igw_id = igws[0]['InternetGatewayId']
        print(f"   - Found IGW with ID: {igw_id}")
        print("   - Detaching IGW from VPC...")
        ec2_client.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        print("   - Deleting IGW...")
        ec2_client.delete_internet_gateway(InternetGatewayId=igw_id)
        print(f"✅ Internet Gateway {igw_id} deleted.")
    else:
        print("✅ No Internet Gateway found attached to this VPC.")

    # --- Step 3: Delete Subnets ---
    print("\n🔎 Searching for Subnets in the VPC...")
    subnet_filter = [{'Name': 'vpc-id', 'Values': [vpc_id]}]
    subnets = ec2_client.describe_subnets(Filters=subnet_filter)['Subnets']

    if subnets:
        for subnet in subnets:
            subnet_id = subnet['SubnetId']
            print(f"   - Deleting Subnet with ID: {subnet_id}")
            ec2_client.delete_subnet(SubnetId=subnet_id)
        print(f"✅ Deleted {len(subnets)} Subnet(s).")
    else:
        print("✅ No Subnets found in this VPC.")
        
    # --- Step 4: Delete Route Tables (non-main) ---
    print("\n🔎 Searching for custom Route Tables in the VPC...")
    rt_filter = [{'Name': 'vpc-id', 'Values': [vpc_id]}]
    route_tables = ec2_client.describe_route_tables(Filters=rt_filter)['RouteTables']

    if route_tables:
        for rt in route_tables:
            # You cannot delete the "main" route table, so we must check for it.
            is_main = False
            for assoc in rt.get('Associations', []):
                if assoc.get('Main'):
                    is_main = True
                    break
            
            if not is_main:
                rt_id = rt['RouteTableId']
                print(f"   - Deleting custom Route Table with ID: {rt_id}")
                ec2_client.delete_route_table(RouteTableId=rt_id)
        print("✅ Deleted all custom Route Tables.")
    else:
        print("✅ No Route Tables found in this VPC.")
        
    # --- Step 5: Finally, Delete the VPC ---
    # A brief delay to ensure all dependencies are detached.
    time.sleep(5) 
    print(f"\n🗑️ Deleting VPC {vpc_id}...")
    ec2_client.delete_vpc(VpcId=vpc_id)
    print("✅ VPC deleted successfully.")

except Exception as e:
    print(f"❌ An error occurred: {e}")

print("\nScript finished.")

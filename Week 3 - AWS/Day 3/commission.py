import boto3

# CLIENT SETUP
# Create a client object for the EC2 service.
# Boto3 will automatically use the credentials from your 'aws configure' setup.
ec2_client = boto3.client('ec2')

print("Script starting...")

# CREATE A VPC

try:
    vpc_response = ec2_client.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = vpc_response['Vpc']['VpcId']
    print(f"✅ VPC created successfully with ID: {vpc_id}")

    # Add a "Name" tag to make it identifiable in the AWS Console
    ec2_client.create_tags(Resources=[vpc_id], Tags=[{
        'Key': 'Name', 
        'Value': 'Boto3-VPC'
        }])
    
    # A "waiter" ensures the VPC is fully available before we proceed
    vpc_waiter = ec2_client.get_waiter('vpc_available')
    vpc_waiter.wait(VpcIds=[vpc_id])
    print("     - VPC is now available.")

except Exception as e:
    print(f"❌ Error creating VPC: {e}")
    exit() # Exit if we can't create the foundation

# CREATE THE SUBNETS
try:
    # Create the Public Subnet
    public_subnet_response = ec2_client.create_subnet(VpcId=vpc_id, CidrBlock='10.0.1.0/24')
    public_subnet_id = public_subnet_response['Subnet']['SubnetId']
    ec2_client.create_tags(Resources=[public_subnet_id], Tags=[{
        'Key': 'Name', 
        'Value': 'Boto3-Public-Subnet'}])
    print(f"✅ Public Subnet created successfully with ID: {public_subnet_id}")

    # Create the Private Subnet
    private_subnet_response = ec2_client.create_subnet(VpcId=vpc_id, CidrBlock='10.0.2.0/24')
    private_subnet_id = private_subnet_response['Subnet']['SubnetId']
    ec2_client.create_tags(Resources=[private_subnet_id], Tags=[{
        'Key': 'Name', 
        'Value': 'Boto3-Private-Subnet'}])
    print(f"✅ Private Subnet created successfully with ID: {private_subnet_id}")
except Exception as e:
    print(f"❌ Error creating subnets: {e}")

# CREATE AND ATTACH THE INTERNET GATEWAY

try:
    # Create the Internet gateway
    igw_response = ec2_client.create_internet_gateway()
    igw_id = igw_response['InternetGateway']['InternetGatewayId']
    ec2_client.create_tags(Resources=[igw_id], Tags=[{
        'Key': 'Name',
        'Value': 'Boto3-IGW'
    }])
    print(f"✅ Internet Gateway created successfully with ID: {igw_id}")

    # Attach the IGW to created VPC
    ec2_client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    print("     - Successfully attached IGW to VPC.")
except Exception as e:
    print(f"❌ Error with Internet Gateway: {e}")

# CREATE AND CONFIGURE THE PUBLIC ROUTE TABLE

try:
    # Create the Public Route Table
    public_rt_response = ec2_client.create_route_table(VpcId=vpc_id)
    public_rt_id = public_rt_response['RouteTable']['RouteTableId']
    ec2_client.create_tags(Resources=[public_rt_id], Tags=[{
        'Key': 'Name',
        'Value': 'Boto3-Public-RT'
    }])
    print(f"✅ Public Route Table created successfully with ID: {public_rt_id}")

    # Create the default route to the Internet Gateway
    ec2_client.create_route(
        RouteTableId=public_rt_id,
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw_id
    )
    print("     - Associated Public RT with Public Subnet.")
except Exception as e:
    print(f"❌ Error with Public Route Table: {e}")

print("\nScript finished for today.")

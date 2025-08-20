import boto3
import os

class aws():
    def __init__(self):
        pass

    def client_setup(self):
        # CLIENT SETUP
        # Create a client object for the EC2 service.
        # Boto3 will automatically use the credentials from your 'aws configure' setup.
        self.ec2_client = boto3.client('ec2')
        print("Script starting...")

    # CREATE A VPC

    def create_vpc(self, cidr):
        try:
            vpc_response = self.ec2_client.create_vpc(CidrBlock=cidr)
            self.vpc_id = vpc_response['Vpc']['VpcId']
            print(f"✅ VPC created successfully with ID: {self.vpc_id}")

            # Add a "Name" tag to make it identifiable in the AWS Console
            self.ec2_client.create_tags(Resources=[self.vpc_id], Tags=[{
                'Key': 'Name', 
                'Value': 'Boto3-VPC'
                }])
            
            # A "waiter" ensures the VPC is fully available before we proceed
            vpc_waiter = self.ec2_client.get_waiter('vpc_available')
            vpc_waiter.wait(VpcIds=[self.vpc_id])
            print("     - VPC is now available.")

        except Exception as e:
            print(f"❌ Error creating VPC: {e}")
            exit() # Exit if we can't create the foundation

    def create_public_subnet(self, public_subnet):
        try:
            # Create the Public Subnet
            self.public_subnet_response = self.ec2_client.create_subnet(VpcId=self.vpc_id, CidrBlock=public_subnet)
            self.public_subnet_id = self.public_subnet_response['Subnet']['SubnetId']
            self.ec2_client.create_tags(Resources=[self.public_subnet_id], Tags=[{
                'Key': 'Name', 
                'Value': 'Boto3-Public-Subnet'}])
            print(f"✅ Public Subnet created successfully with ID: {self.public_subnet_id}")
        except Exception as e:
            print(f"❌ Error creating public subnet: {e}")

    def create_private_subnet(self, private_subnet):
        try:
            # Create the Private Subnet
            self.private_subnet_response = self.ec2_client.create_subnet(VpcId=self.vpc_id, CidrBlock=private_subnet)
            self.private_subnet_id = self.private_subnet_response['Subnet']['SubnetId']
            self.ec2_client.create_tags(Resources=[self.private_subnet_id], Tags=[{
                'Key': 'Name', 
                'Value': 'Boto3-Private-Subnet'}])
            print(f"✅ Private Subnet created successfully with ID: {self.private_subnet_id}")
        except Exception as e:
            print(f"❌ Error creating subnets: {e}")

    # CREATE AND ATTACH THE INTERNET GATEWAY
    def create_igw(self):
        try:
            # Create the Internet gateway
            igw_response = self.ec2_client.create_internet_gateway()
            self.igw_id = igw_response['InternetGateway']['InternetGatewayId']
            self.ec2_client.create_tags(Resources=[self.igw_id], Tags=[{
                'Key': 'Name',
                'Value': 'Boto3-IGW'
            }])
            print(f"✅ Internet Gateway created successfully with ID: {self.igw_id}")
        except Exception as e:
            print(f"❌ Error with Internet Gateway: {e}")

    def attach_igw_to_vpc(self):
        try:
            # Attach the IGW to created VPC
            self.ec2_client.attach_internet_gateway(InternetGatewayId=self.igw_id, VpcId=self.vpc_id)
            print("     - Successfully attached IGW to VPC.")
        except Exception as e:
            print(f"❌ Error with Internet Gateway: {e}")

    # CREATE AND CONFIGURE THE PUBLIC ROUTE TABLE
    def create_public_route_table(self):
        try:
            # Create the Public Route Table
            self.public_rt_response = self.ec2_client.create_route_table(VpcId=self.vpc_id)
            self.public_rt_id = self.public_rt_response['RouteTable']['RouteTableId']
            self.ec2_client.create_tags(Resources=[self.public_rt_id], Tags=[{
                'Key': 'Name',
                'Value': 'Boto3-Public-RT'
            }])
            print(f"✅ Public Route Table created successfully with ID: {self.public_rt_id}")
        except Exception as e:
            print(f"❌ Error with Public Route Table: {e}")

    def create_public_table_route(self, route):
        try:
            # Create the default route to the Internet Gateway
            self.ec2_client.create_route(
                RouteTableId=self.public_rt_id,
                DestinationCidrBlock=route,
                GatewayId=self.igw_id
            )
            print("     - Associated Public RT with Public Subnet.")

            # Associate Route Table with Public Subnet
            self.ec2_client.associate_route_table(
                RouteTableId=self.public_rt_id,
                SubnetId=self.public_subnet_id
            )
        except Exception as e:
            print(f"❌ Error with Public Route Table: {e}")

    # CREATE THE NAT GATEWAY FOR THE PRIVATE SUBNET
    def create_nat_gateway(self):
        try:
            # Create an Elastic IP
            self.eip_response = self.ec2_client.allocate_address(Domain='vpc')
            self.eip_alloc_id = self.eip_response['AllocationId']
            print(f"✅ Elastic IP created successfully with Allocation ID: {self.eip_alloc_id}")

            # Create the NAT Gateway
            self.nat_gw_respone = self.ec2_client.create_nat_gateway(
                SubnetId=self.public_subnet_id,
                AllocationId=self.eip_alloc_id
            )
            self.nat_gw_id = self.nat_gw_respone['NatGateway']['NatGatewayId']
            self.ec2_client.create_tags(Resources=[self.nat_gw_id], Tags=[{
                'Key': 'Name',
                'Value': 'Boto3-NAT-GW'
            }])
            print(f"✅ NAT Gateway created successfully with ID: {self.nat_gw_id}")

            # CRITICAL: Wait for the NAT Gateway to become fully available. This can take a minute or two.
            print("     - Waiting for NAT Gateway to become available...")
            nat_waiter = self.ec2_client.get_waiter('nat_gateway_available')
            nat_waiter.wait(NatGatewayIds=[self.nat_gw_id])
            print("     - NAT Gateway is now available.")
        except Exception as e:
            print(f"❌ Error creating NAT Gateway: {e}")

    # CREATE AND CONFIGURE PRIVATE ROUTE TABLE
    def create_private_route_table(self):
        try:
            # Create the Private Route Table
            self.private_rt_response = self.ec2_client.create_route_table(VpcId=self.vpc_id)
            self.private_rt_id = self.private_rt_response['RouteTable']['RouteTableId']
            self.ec2_client.create_tags(Resources=[self.private_rt_id], Tags=[{
                'Key': 'Name',
                'Value': 'Boto3-Private-RT'
            }])
            print(f"✅ Private Route Table created successfully with ID: {self.private_rt_id}")
        except Exception as e:
            print(f"❌ Error with Private Route Table: {e}")

    def create_private_table_route(self, route):
        try:
            # Create the route to the NAT Gateway
            self.ec2_client.create_route(
                RouteTableId=self.private_rt_id,
                DestinationCidrBlock=route,
                NatGatewayId=self.nat_gw_id
            )
            print(f"     - Added route {route} -> NAT Gateway.")

            # Associate Route Table with Private Subnet
            self.ec2_client.associate_route_table(
                RouteTableId=self.private_rt_id,
                SubnetId=self.private_subnet_id
            )
            print("     - Associated Private RT with Private Subnet.")
        except Exception as e:
            print(f"❌ Error with Private Route Table: {e}")

    # CREATE THE SECURITY GROUPS
    def web_server_security_group(self):
        # Create the Web Server Security Group
        self.web_sg_response = self.ec2_client.create_security_group(
            GroupName='Boto3-Web-SG',
            Description='Allow HTTP and SSH access',
            VpcId=self.vpc_id
        )
        self.web_sg_id = self.web_sg_response['GroupId']
        print(f"✅ Web Server Security Group created successfully with ID: {self.web_sg_id}")

        # Add inbound rules to the Web Server SG
        self.ec2_client.authorize_security_group_ingress(
            GroupId=self.web_sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        print("     - Added HTTP and SSH ingress rules to Web SG.")

    def database_server_security_group(self):
        try:
            # Create the Database Server Security Group
            self.database_sg_response = self.ec2_client.create_security_group(
                GroupName='Boto3-Database-SG',
                Description='Allow MySQL and SSH access',
                VpcId=self.vpc_id
            )
            self.database_sg_id = self.database_sg_response['GroupId']
            print(f"✅ Database Server Security Group created successfully with ID: {self.database_sg_id}")

            # Add inbound rules to the Database Server SG
            self.ec2_client.authorize_security_group_ingress(
                GroupId=self.database_sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp', 'FromPort': 3306, 'ToPort': 3306, 'UserIdGroupPairs': [{'GroupId': self.web_sg_id}]
                    },
                    {
                        'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'UserIdGroupPairs': [{'GroupId': self.web_sg_id}]
                    }
                ]
            )
            print("     - Added MySQL and SSH ingress rules to Database SG.")
        except Exception as e:
            print(f"❌ Error creating Security Groups: {e}")

    

    # Add this inside your 'aws' class

    def create_ec2_key_pair(self, key_name='boto3-lab-key'):
        """
        Creates an EC2 key pair if it doesn't exist and saves the private key.
        """
        self.key_name = key_name
        private_key_file = f"{self.key_name}.pem"

        # Check if the key file already exists locally
        if os.path.exists(private_key_file):
            print(f"✅ Key pair '{self.key_name}' already exists locally. Skipping creation.")
            return

        try:
            print(f"🔎 Checking for existing key pair named '{self.key_name}' in AWS...")
            # This will error if the key doesn't exist, which is what we want.
            self.ec2_client.describe_key_pairs(KeyNames=[self.key_name])
            print(f"   - Key pair found in AWS but not locally. Please manage keys manually or delete from AWS.")
            # For a robust script, you might delete and recreate, but for a lab, this is safer.
            return
            
        except self.ec2_client.exceptions.ClientError as e:
            if 'InvalidKeyPair.NotFound' in str(e):
                print(f"   - Key pair not found. Creating a new one...")
                key_pair_response = self.ec2_client.create_key_pair(KeyName=self.key_name)
                
                # Save the private key to a .pem file
                with open(private_key_file, 'w') as f:
                    f.write(key_pair_response['KeyMaterial'])
                
                # Set permissions for the key file (important for Linux/macOS)
                os.chmod(private_key_file, 0o400)
                
                print(f"✅ Key pair '{self.key_name}' created and saved to '{private_key_file}'.")
            else:
                raise e

    def _get_latest_amazon_linux_ami(self):
        """
        Finds the ID of the most recent Amazon Linux 2 AMI.
        """
        try:
            print("🔎 Finding the latest Amazon Linux 2 AMI...")
            response = self.ec2_client.describe_images(
                Owners=['amazon'],
                Filters=[
                    {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                    {'Name': 'state', 'Values': ['available']},
                ]
            )
            # Sort images by creation date to find the newest one
            images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
            ami_id = images[0]['ImageId']
            print(f"   - Found AMI ID: {ami_id}")
            return ami_id
        except Exception as e:
            print(e)

    def create_ec2_instances(self):
        # Creates the Web and Database EC2 instances.
        try:
            # First, get the latest AMI ID so our script is always up-to-date
            ami_id = self._get_latest_amazon_linux_ami()

            # --- Launch the Web Server in the Public Subnet ---
            print("🚀 Launching Web Server instance...")
            web_instance_response = self.ec2_client.run_instances(
                ImageId=ami_id,
                InstanceType='t2.micro',  # Free tier eligible
                KeyName=self.key_name,
                MaxCount=1,
                MinCount=1,
                NetworkInterfaces=[{
                    'DeviceIndex': 0,
                    'SubnetId': self.public_subnet_id,
                    'Groups': [self.web_sg_id],
                    'AssociatePublicIpAddress': True  # Give it a public IP
                }],
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': 'Boto3-Web-Server'}]
                }]
            )
            web_instance_id = web_instance_response['Instances'][0]['InstanceId']
            print(f"✅ Web Server instance launched with ID: {web_instance_id}")

            # --- Launch the Database Server in the Private Subnet ---
            print("🚀 Launching Database Server instance...")
            db_instance_response = self.ec2_client.run_instances(
                ImageId=ami_id,
                InstanceType='t2.micro',
                KeyName=self.key_name,
                MaxCount=1,
                MinCount=1,
                NetworkInterfaces=[{
                    'DeviceIndex': 0,
                    'SubnetId': self.private_subnet_id,
                    'Groups': [self.database_sg_id],
                    'AssociatePublicIpAddress': False # NO public IP
                }],
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': 'Boto3-Database-Server'}]
                }]
            )
            db_instance_id = db_instance_response['Instances'][0]['InstanceId']
            print(f"✅ Database Server instance launched with ID: {db_instance_id}")
            
            # --- Wait for instances to be running ---
            print("     - Waiting for instances to enter the 'running' state...")
            waiter = self.ec2_client.get_waiter('instance_running')
            waiter.wait(InstanceIds=[web_instance_id, db_instance_id])
            print("✅ Both instances are now running.")

            # Get the public IP of the web server to display it
            desc_response = self.ec2_client.describe_instances(InstanceIds=[web_instance_id])
            public_ip = desc_response['Reservations'][0]['Instances'][0]['PublicIpAddress']
            print(f"\n🌐 You can connect to the Web Server via SSH: ssh -i '{self.key_name}.pem' ec2-user@{public_ip}")

        except Exception as e:
            print(f"❌ Error creating EC2 instances: {e}")


def main():
    cidr = '10.0.0.0/16'
    public_subnet = '10.0.1.0/24'
    private_subnet = '10.0.2.0/24'
    public_table_route = '0.0.0.0/0'
    private_table_route = '0.0.0.0/0'

    aws_client = aws()
    aws_client.client_setup()
    aws_client.create_vpc(cidr=cidr)
    aws_client.create_public_subnet(public_subnet=public_subnet)
    aws_client.create_private_subnet(private_subnet=private_subnet)
    aws_client.create_igw()
    aws_client.attach_igw_to_vpc()
    aws_client.create_public_route_table()
    aws_client.create_public_table_route(route=public_table_route)
    aws_client.create_nat_gateway()
    aws_client.create_private_route_table()
    aws_client.create_private_table_route(route=private_table_route)
    aws_client.web_server_security_group()
    aws_client.database_server_security_group()

    aws_client.create_ec2_key_pair() # Creates the key pair
    aws_client.create_ec2_instances() # Creates the instances

    print("\n🚀 Full two-tier network architecture successfully deployed!")

if __name__ == '__main__':
    main()

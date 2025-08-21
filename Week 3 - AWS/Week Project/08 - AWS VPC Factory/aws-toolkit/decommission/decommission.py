import boto3
import os
import stat

class Destroy():
    def __init__(self):
        pass

    def find_vpc(self):
        # Create a client object for the EC2 service
        self.ec2_client = boto3.client('ec2')

        # --- CONFIGURATION ---
        self.VPC_NAME_TAG = 'Boto3-VPC'
        self.KEY_PAIR_NAME = 'boto3-lab-key' # The name of the key pair your factory script creates

        print("Script starting...")

        try:
            # --- Step 1: Find the VPC ID ---
            print(f"🔎 Searching for VPC with Name tag: {self.VPC_NAME_TAG}...")
            self.vpcs = self.ec2_client.describe_vpcs(Filters=[{'Name': 'tag:Name', 'Values': [self.VPC_NAME_TAG]}])['Vpcs']

            if not self.vpcs:
                print(f"✅ No VPC found with the name '{self.VPC_NAME_TAG}'. Nothing to do.")
                exit()

            self.vpc_id = self.vpcs[0]['VpcId']
            print(f"   - Found VPC with ID: {self.vpc_id}")
        except Exception as e:
            print(f"❌ Failed to find VPC {e}")

    def terminate_instances(self):
        # --- Step 2: Terminate EC2 instances ---
        print("\n🔎 Searching for and terminating EC2 instances in the VPC...")
        self.instance_filter = [{'Name': 'vpc-id', 'Values': [self.vpc_id]}]
        self.reservations = self.ec2_client.describe_instances(Filters=self.instance_filter)['Reservations']
        
        self.instance_ids = [inst['InstanceId'] for res in self.reservations for inst in res['Instances']]

        try:
            if self.instance_ids:
                self.ec2_client.terminate_instances(InstanceIds=self.instance_ids)
                waiter = self.ec2_client.get_waiter('instance_terminated')
                print(f"   - Waiting for {len(self.instance_ids)} instance(s) to terminate...")
                waiter.wait(InstanceIds=self.instance_ids)
                print("✅ All EC2 instances terminated.")
            else:
                print("✅ No EC2 instances found.")
        except Exception as e:
            print(f"❌ Failed to terminate instances {e}")

    def delete_nat_gateways(self):
        # --- Step 3: Delete NAT Gateways ---
        print("\n🔎 Searching for and deleting NAT Gateways in the VPC...")
        self.nat_gw_filter = [{'Name': 'vpc-id', 'Values': [self.vpc_id]}, {'Name': 'state', 'Values': ['pending', 'available']}]
        nat_gateways = self.ec2_client.describe_nat_gateways(Filters=self.nat_gw_filter)['NatGateways']

        try:
            if nat_gateways:
                for nat_gw in nat_gateways:
                    nat_gw_id = nat_gw['NatGatewayId']
                    self.ec2_client.delete_nat_gateway(NatGatewayId=nat_gw_id)
                    waiter = self.ec2_client.get_waiter('nat_gateway_deleted')
                    print(f"   - Waiting for NAT Gateway {nat_gw_id} to be deleted...")
                    waiter.wait(NatGatewayIds=[nat_gw_id])
                    print(f"✅ NAT Gateway {nat_gw_id} deleted.")
            else:
                print("✅ No active NAT Gateways found.")
        except Exception as e:
            print(f"❌ Failed deleting NAT gateway {e}")

    def release_elastic_ip(self):
        # --- Step 4: Release Elastic IPs ---
        print("\n🔎 Searching for and releasing unassociated Elastic IPs...")
        self.eips = self.ec2_client.describe_addresses(Filters=[{'Name': 'domain', 'Values': ['vpc']}])['Addresses']
        
        self.eips_released = 0
        try:
            if self.eips:
                for eip in self.eips:
                    if "AssociationId" not in eip and "InstanceId" not in eip:
                        self.ec2_client.release_address(AllocationId=eip['AllocationId'])
                        self.eips_released += 1
                if self.eips_released > 0:
                    print(f"✅ Released {self.eips_released} Elastic IP(s).")
                else:
                    print("✅ No unassociated Elastic IPs found to release.")
            else:
                print("✅ No Elastic IPs found in this account.")
        except Exception as e:
            print(f"❌ Failed to release elastic IP {e}")

    def detach_delete_igw(self):
        # --- Step 5: Detach and Delete Internet Gateways ---
        print("\n🔎 Searching for and deleting Internet Gateways...")
        self.igw_filter = [{'Name': 'attachment.vpc-id', 'Values': [self.vpc_id]}]
        self.igws = self.ec2_client.describe_internet_gateways(Filters=self.igw_filter)['InternetGateways']

        try:
            if self.igws:
                for igw in self.igws:
                    self.igw_id = igw['InternetGatewayId']
                    self.ec2_client.detach_internet_gateway(InternetGatewayId=self.igw_id, VpcId=self.vpc_id)
                    self.ec2_client.delete_internet_gateway(InternetGatewayId=self.igw_id)
                print(f"✅ Deleted {len(self.igws)} Internet Gateway(s).")
            else:
                print("✅ No Internet Gateway found.")
        except Exception as e:
            print(f"❌ Failed to detach and delete internet gateway {e}")

    def delete_subnets(self):
        # --- Step 6: Delete Subnets ---
        print("\n🔎 Searching for and deleting Subnets...")
        self.subnets = self.ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [self.vpc_id]}])['Subnets']

        try:
            if self.subnets:
                for subnet in self.subnets:
                    self.ec2_client.delete_subnet(SubnetId=subnet['SubnetId'])
                print(f"✅ Deleted {len(self.subnets)} Subnet(s).")
            else:
                print("✅ No Subnets found.")
        except Exception as e:
            print(f"❌ Failure deleting subnets {e}")

    def delete_route_tables(self):
        # Step 7: Delete Custom Route Tables
        print("\n🔎 Searching for and deleting custom Route Tables...")
        self.route_tables = self.ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [self.vpc_id]}])['RouteTables']
        
        try:
            if self.route_tables:
                for rt in self.route_tables:
                    if not any(assoc.get('Main', False) for assoc in rt.get('Associations', [])):
                        self.ec2_client.delete_route_table(RouteTableId=rt['RouteTableId'])
                print("✅ Deleted all custom Route Tables.")
            else:
                print("✅ No custom Route Tables found.")
        except Exception as e:
            print(f"❌ Failed deleting route tables {e}")

    def delete_security_groups(self):
        # Step 8: Delete Custom Security Groups
        print("\n🔎 Searching for and deleting custom Security Groups...")
        self.sgs = self.ec2_client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [self.vpc_id]}])['SecurityGroups']
        
        try:
            if self.sgs:
                for sg in self.sgs:
                    if sg['GroupName'] != 'default':
                        try:
                            self.ec2_client.delete_security_group(GroupId=sg['GroupId'])
                        except Exception as e:
                            print(f"   - Could not delete SG {sg['GroupId']} (might have dependent rules): {e}")
                print("✅ Deleted all custom Security Groups.")
            else:
                print("✅ No custom Security Groups found.")
        except Exception as e:
            print(f"❌ Failed to delete security groups {e}")

    def delete_vpc(self):
        # Step 9: Delete the VPC
        print(f"\n🗑️ Deleting VPC {self.vpc_id}...")
        try:
            self.ec2_client.delete_vpc(VpcId=self.vpc_id)
            print("✅ VPC deleted successfully.")
        except Exception as e:
            print(f"❌ Failed to delete VPC {e}")

    def delete_ec2_key_pair(self):
        # --- Final Step: Delete the EC2 Key Pair ---
        print(f"\n🔑 Searching for and deleting EC2 key pair '{self.KEY_PAIR_NAME}'...")
        try:
            # First, delete the key from AWS
            self.ec2_client.delete_key_pair(KeyName=self.KEY_PAIR_NAME)
            print(f"✅ EC2 key pair '{self.KEY_PAIR_NAME}' deleted from AWS.")
            
        except self.ec2_client.exceptions.ClientError as e:
            if 'InvalidKeyPair.NotFound' in str(e):
                print(f"✅ Key pair '{self.KEY_PAIR_NAME}' not found in AWS. Nothing to delete.")
            else:
                # Re-raise the exception if it's a different error
                print(f"❌ An error occurred deleting the key pair from AWS: {e}")

        # Now, handle the local file
        try:
            self.key_file = f"{self.KEY_PAIR_NAME}.pem"
            if os.path.exists(self.key_file):
                # THIS IS THE FIX: Make the file writable before deleting
                print(f"   - Making local key file '{self.key_file}' writable...")
                os.chmod(self.key_file, stat.S_IWRITE) # Or you can use 0o600
                
                # Now, delete the file
                os.remove(self.key_file)
                print(f"✅ Local key file '{self.key_file}' deleted.")
                
        except Exception as e:
            print(f"❌ An error occurred deleting the local key file: {e}")

def main():
    aws_destroyer = Destroy()
    aws_destroyer.find_vpc()
    aws_destroyer.terminate_instances()
    aws_destroyer.delete_nat_gateways()
    aws_destroyer.release_elastic_ip()
    aws_destroyer.detach_delete_igw()
    aws_destroyer.delete_subnets()
    aws_destroyer.delete_route_tables()
    aws_destroyer.delete_security_groups()
    aws_destroyer.delete_vpc()
    aws_destroyer.delete_ec2_key_pair()

    print("\nDestroyer Script finished.")

if __name__ == '__main__':
    main()

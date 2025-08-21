# create_security_group.py
import boto3
import argparse

def create_security_group(ec2_client, vpc_id, name, description, allow_http=False, allow_ssh=False, allow_mysql_from_sg=None):
    print(f"Creating Security Group '{name}' in VPC {vpc_id}...")
    try:
        sg_response = ec2_client.create_security_group(
            GroupName=name,
            Description=description,
            VpcId=vpc_id
        )
        sg_id = sg_response['GroupId']
        print(f"✅ Security Group created with ID: {sg_id}")

        # Build the list of permissions
        ip_permissions = []
        if allow_http:
            ip_permissions.append({'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]})
            print("   - Adding rule: Allow HTTP from Anywhere")
        if allow_ssh:
            # WARNING: Allowing SSH from 0.0.0.0/0 is insecure. Use for labs only.
            ip_permissions.append({'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]})
            print("   - Adding rule: Allow SSH from Anywhere (INSECURE)")
        if allow_mysql_from_sg:
            ip_permissions.append({'IpProtocol': 'tcp', 'FromPort': 3306, 'ToPort': 3306, 'UserIdGroupPairs': [{'GroupId': allow_mysql_from_sg}]})
            print(f"   - Adding rule: Allow MySQL from Security Group {allow_mysql_from_sg}")

        # Authorize the rules if any were defined
        if ip_permissions:
            ec2_client.authorize_security_group_ingress(GroupId=sg_id, IpPermissions=ip_permissions)
            print("✅ Ingress rules applied successfully.")
        
        print(f"   - Security Group ID: {sg_id}")
        return sg_id
        
    except Exception as e:
        print(f"❌ Error creating Security Group: {e}")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a Security Group with optional inbound rules.")
    parser.add_argument('--vpc-id', required=True, help='VPC ID to create the SG in.')
    parser.add_argument('--name', required=True, help='Name for the Security Group (e.g., Web-SG).')
    parser.add_argument('--desc', required=True, help='Description for the Security Group.')
    parser.add_argument('--allow-http', action='store_true', help='Add a rule to allow HTTP (port 80) from anywhere.')
    parser.add_argument('--allow-ssh', action='store_true', help='Add a rule to allow SSH (port 22) from anywhere.')
    parser.add_argument('--allow-mysql-from', type=str, help='Source Security Group ID to allow MySQL (port 3306) from.')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    create_security_group(client, args.vpc_id, args.name, args.desc, args.allow_http, args.allow_ssh, args.allow_mysql_from)
    
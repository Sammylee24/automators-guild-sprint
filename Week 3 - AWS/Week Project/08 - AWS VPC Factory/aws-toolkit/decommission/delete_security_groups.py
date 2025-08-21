# delete_security_groups.py
import boto3
import argparse

def delete_custom_security_groups_in_vpc(ec2_client, vpc_id):
    try:
        sgs = ec2_client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['SecurityGroups']

        if not sgs:
            print(f"✅ No Security Groups found in VPC {vpc_id}.")
            return
            
        deleted_count = 0
        print(f"Searching for custom Security Groups in VPC {vpc_id}...")
        for sg in sgs:
            # You cannot delete the "default" security group.
            if sg['GroupName'] != 'default':
                sg_id = sg['GroupId']
                print(f"   - Deleting custom Security Group {sg_id} ({sg['GroupName']})...")
                try:
                    ec2_client.delete_security_group(GroupId=sg_id)
                    deleted_count += 1
                except Exception as e:
                    print(f"     - ⚠️ Could not delete SG {sg_id}. It might have dependent resources or rules. Error: {e}")

        if deleted_count > 0:
            print(f"✅ Deleted {deleted_count} custom Security Group(s).")
        else:
            print("✅ No custom Security Groups found to delete.")
    except Exception as e:
        print(f"❌ Error deleting Security Groups: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Delete all custom (non-default) Security Groups within a VPC.")
    parser.add_argument('--vpc-id', required=True, help='The ID of the VPC.')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    delete_custom_security_groups_in_vpc(client, args.vpc_id)
    
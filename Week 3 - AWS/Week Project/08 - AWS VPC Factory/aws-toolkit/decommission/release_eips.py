# release_eips.py
import boto3

def release_unassociated_eips(ec2_client):
    try:
        eips = ec2_client.describe_addresses(Filters=[{'Name': 'domain', 'Values': ['vpc']}])['Addresses']
        
        released_count = 0
        for eip in eips:
            if "AssociationId" not in eip and "InstanceId" not in eip:
                print(f"Releasing Elastic IP with Allocation ID: {eip['AllocationId']}...")
                ec2_client.release_address(AllocationId=eip['AllocationId'])
                released_count += 1
        
        if released_count > 0:
            print(f"✅ Released {released_count} Elastic IP(s).")
        else:
            print("✅ No unassociated Elastic IPs found to release.")
    except Exception as e:
        print(f"❌ Error releasing Elastic IPs: {e}")

if __name__ == '__main__':
    client = boto3.client('ec2')
    release_unassociated_eips(client)
    
# delete_route_tables.py
import boto3
import argparse

def delete_custom_route_tables_in_vpc(ec2_client, vpc_id):
    try:
        route_tables = ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['RouteTables']
        
        if not route_tables:
            print(f"✅ No Route Tables found in VPC {vpc_id}.")
            return

        deleted_count = 0
        print(f"Searching for custom Route Tables in VPC {vpc_id}...")
        for rt in route_tables:
            # Check if the route table is the "main" one, which cannot be deleted.
            is_main = any(assoc.get('Main', False) for assoc in rt.get('Associations', []))
            if not is_main:
                rt_id = rt['RouteTableId']
                print(f"   - Deleting custom Route Table {rt_id}...")
                ec2_client.delete_route_table(RouteTableId=rt_id)
                deleted_count += 1
        
        if deleted_count > 0:
            print(f"✅ Deleted {deleted_count} custom Route Table(s).")
        else:
            print("✅ No custom Route Tables found to delete.")
    except Exception as e:
        print(f"❌ Error deleting Route Tables: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Delete all custom (non-main) Route Tables within a VPC.")
    parser.add_argument('--vpc-id', required=True, help='The ID of the VPC.')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
   
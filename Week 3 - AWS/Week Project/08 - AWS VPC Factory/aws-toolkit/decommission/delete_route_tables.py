# delete_route_tables.py (Updated and Corrected)
import boto3
import argparse

def delete_custom_route_tables_in_vpc(ec2_client, vpc_id):
    """
    Finds and deletes all custom (non-main) route tables in a VPC.
    It first disassociates them from any subnets to resolve dependencies.
    """
    try:
        route_tables = ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['RouteTables']
        
        if not route_tables:
            print(f"✅ No Route Tables found in VPC {vpc_id}.")
            return

        deleted_count = 0
        print(f"🔎 Searching for custom Route Tables in VPC {vpc_id}...")
        for rt in route_tables:
            rt_id = rt['RouteTableId']
            
            # Check if the route table is the "main" one, which we must not delete.
            is_main = any(assoc.get('Main', False) for assoc in rt.get('Associations', []))
            
            if not is_main:
                print(f"   - Found custom Route Table: {rt_id}")
                
                # --- THIS IS THE NEW, CRITICAL LOGIC ---
                # Step 1: Disassociate from any subnets
                for assoc in rt.get('Associations', []):
                    # We only care about explicit subnet associations, not the 'main' one
                    if not assoc.get('Main'):
                        assoc_id = assoc['RouteTableAssociationId']
                        print(f"     - Disassociating from subnet (Association ID: {assoc_id})...")
                        try:
                            ec2_client.disassociate_route_table(AssociationId=assoc_id)
                        except Exception as disassoc_e:
                            print(f"       - ⚠️ Could not disassociate {assoc_id}: {disassoc_e}")
                # --- END OF NEW LOGIC ---

                # Step 2: Now that it's disassociated, delete the route table
                try:
                    print(f"     - Deleting Route Table {rt_id}...")
                    ec2_client.delete_route_table(RouteTableId=rt_id)
                    deleted_count += 1
                except Exception as delete_e:
                    print(f"       - ⚠️ Could not delete Route Table {rt_id}: {delete_e}")

        if deleted_count > 0:
            print(f"✅ Deleted {deleted_count} custom Route Table(s).")
        else:
            print("✅ No custom Route Tables found to delete.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Delete all custom (non-main) Route Tables within a VPC.")
    parser.add_argument('--vpc-id', required=True, help='The ID of the VPC.')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    delete_custom_route_tables_in_vpc(client, args.vpc_id)
    
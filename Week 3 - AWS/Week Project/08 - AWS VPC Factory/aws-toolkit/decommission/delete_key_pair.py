# delete_key_pair.py (Updated and Corrected)
import boto3
import os
import stat
import argparse

def delete_key_pair(ec2_client, key_name, key_path):
    # First, try to delete the key pair from AWS
    try:
        print(f"🔑 Deleting key pair '{key_name}' from AWS...")
        ec2_client.delete_key_pair(KeyName=key_name)
        print(f"✅ EC2 key pair '{key_name}' deleted from AWS.")
    except ec2_client.exceptions.ClientError as e:
        if 'InvalidKeyPair.NotFound' in str(e):
            print(f"✅ Key pair '{key_name}' not found in AWS. Nothing to delete.")
        else:
            print(f"❌ An AWS error occurred deleting the key pair: {e}")
            
    # Now, handle the local .pem file at the specified path
    try:
        # Construct the full path to the key file
        full_key_path = os.path.join(key_path, f"{key_name}.pem")
        
        if os.path.exists(full_key_path):
            print(f"   - Found local key file at '{full_key_path}'")
            print(f"   - Making local key file writable...")
            os.chmod(full_key_path, stat.S_IWRITE)
            
            print(f"   - Deleting local key file...")
            os.remove(full_key_path)
            print(f"✅ Local key file '{full_key_path}' deleted.")
        else:
            print(f"✅ Local key file not found at '{full_key_path}'. Nothing to delete.")
            
    except Exception as e:
        print(f"❌ An error occurred deleting the local key file: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Delete an EC2 Key Pair from AWS and a local .pem file.")
    parser.add_argument('--key-name', required=True, help='The name of the key pair (e.g., boto3-lab-key).')
    
    # --- THIS IS THE FIX ---
    # The new default path correctly goes up one level, then into the 'commission' folder.
    parser.add_argument('--key-path', default='../commission', help='The path to the directory where the .pem file is stored.')
    # --- END OF FIX ---
    
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    delete_key_pair(client, args.key_name, args.key_path)
    
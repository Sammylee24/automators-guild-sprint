# create_key_pair.py
import boto3
import os
import stat
import argparse

def create_key_pair(ec2_client, key_name):
    """
    Creates an EC2 key pair if it doesn't exist and saves the private key.
    """
    private_key_file = f"{key_name}.pem"

    # Check if the local .pem file already exists
    if os.path.exists(private_key_file):
        print(f"✅ Key file '{private_key_file}' already exists locally. Skipping.")
        return True

    try:
        # Check if the key pair exists in AWS
        ec2_client.describe_key_pairs(KeyNames=[key_name])
        print(f"⚠️ Key pair '{key_name}' exists in AWS but the .pem file is missing locally.")
        print("   - Please delete the key from AWS manually and re-run.")
        return False
        
    except ec2_client.exceptions.ClientError as e:
        if 'InvalidKeyPair.NotFound' in str(e):
            print(f"🔎 Key pair '{key_name}' not found in AWS. Creating a new one...")
            try:
                key_pair_response = ec2_client.create_key_pair(KeyName=key_name)
                
                # Save the private key material to the .pem file
                with open(private_key_file, 'w') as f:
                    f.write(key_pair_response['KeyMaterial'])
                
                # Set permissions to read-only for the owner (best practice)
                os.chmod(private_key_file, stat.S_IREAD) # S_IREAD is for Windows read-only
                
                print(f"✅ Key pair '{key_name}' created and saved to '{private_key_file}'.")
                return True
            except Exception as create_e:
                print(f"❌ Failed to create key pair: {create_e}")
                return False
        else:
            # A different ClientError occurred
            print(f"❌ An AWS error occurred: {e}")
            return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create an EC2 Key Pair.")
    parser.add_argument('--key-name', required=True, help='The name for the new key pair (e.g., my-lab-key).')
    args = parser.parse_args()
    
    client = boto3.client('ec2')
    create_key_pair(client, args.key_name)
    
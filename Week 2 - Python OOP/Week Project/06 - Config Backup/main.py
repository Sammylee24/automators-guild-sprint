from netmiko import ConnectHandler
import logging
import sys
import os
from datetime import datetime
from device_list import devices
import argparse

class NetworkDevice():
    def __init__(self, ip, user, password, device_type, port):
        self.ip = ip
        self.user = user
        self.password = password
        self.device_type = device_type
        self.port = port

    def connect(self):
        try:
            device_params = {
                'host': self.ip,
                'username': self.user,
                'password': self.password,
                'port': self.port,
                'device_type': self.device_type
            }
            self.ssh = ConnectHandler(**device_params)
            logging.info(f"Connected to {self.ip}")
        except Exception as e:
            logging.error(f"Error connecting to {self.ip}")
            sys.exit(1)

    def enable(self, dev_type):
        try:
            if self.device_type == dev_type:
                self.ssh.enable()
                logging.info(f"Enabled {self.ip} successfully.")
        except Exception as e:
            logging.error(f"Error enabling {self.ip}")
            sys.exit(1)

    def backup_config(self, backup_dir="backups"):
        try:
            # Step 1 – Get running config
            output = self.ssh.send_command("show running-config")
            
            # Step 2 – Ensure backup directory exists
            os.makedirs(backup_dir, exist_ok=True)
            
            # Step 3 – Create timestamped file name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(backup_dir, f"{self.ip}_{timestamp}.txt")
            
            # Step 4 – Write output to file
            with open(filename, "w") as f:
                f.write(output)
            
            logging.info(f"Backed up config for {self.ip} to {filename}")
        
        except Exception as e:
            logging.error(f"Error backing up config for {self.ip}: {e}")

    def disconnect(self):
        try:
            self.ssh.disconnect()
            logging.info(f"Successfully disconnected from {self.ip}")
        except Exception as e:
            logging.error(f"Failure disconnecting from {self.ip}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Network Automation Script")
    
    parser.add_argument(
        "--log",
        default="log.txt",
        help="Log file path"
    )
    parser.add_argument(
        "--vendor",
        default='cisco-ios',
        help="What device vendor?"
    )

    args = parser.parse_args()

    logging.basicConfig(
            filename=args.log,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
        )

    for dev in devices:
        device = NetworkDevice(
            ip=dev['host'],
            user=dev['username'],
            password=dev['password'],
            device_type=dev['device_type'],
            port=dev['port']
        )

        device.connect()
        device.enable(dev_type=args.vendor)
        device.backup_config(backup_dir="backups")
        device.disconnect()

if __name__ == "__main__":
    main()

import logging
import netmiko as nk
from datetime import datetime

# Configure logging to write to a file
logging.basicConfig(
    filename='log_file.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# List of devices
devices = [
    {
        'device_type': 'cisco_ios',
        'host': '192.168.2.137',
        'username': 'Samuel',
        'password': 'Samuel@123',
        'port': 22
    },
    {
        'device_type': 'cisco_ios',
        'host': '192.168.2.138',
        'username': 'Samuel',
        'password': 'Samuel@123',
        'port': 22
    },
    {
        'device_type': 'cisco_ios',
        'host': '192.168.2.139',
        'username': 'Samuel',
        'password': 'Samuel@123',
        'port': 22
    },
    {
        'device_type': 'cisco_ios',
        'host': '192.168.2.140',
        'username': 'Samuel',
        'password': 'Samuel@123',
        'port': 22
    }
]

# Loop through each device
for device in devices:
    try:
        ssh = nk.ConnectHandler(**device)
        ssh.enable()
        output = ssh.send_command('show ip int brief')
        ssh.disconnect()

        # Log the output
        logging.info(f"[{device['host']}] Show IP Int Brief:\n{output}\n")

    except Exception as e:
        logging.error(f"[{device['host']}] Connection failed: {e}")

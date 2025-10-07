# Import relevant libraries
from netmiko import ConnectHandler

# Device parameters
router = {
    'device_type': 'cisco_ios',
    'host': '192.168.220.50',
    'username': 'Samuel',
    'password': 'Samuel@123',
    'port': 22
}

# Connect to device
ssh = ConnectHandler(**router)

# Enter device enable mode
ssh.enable()

# Execute command on device
result = ssh.send_command('show ip int b')
print(result)

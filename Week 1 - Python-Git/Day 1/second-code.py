# Import relevant libraries
from netmiko import ConnectHandler

# Devices login parameters in a list
devices = [
    {
    'device_type': 'cisco_ios',
    'host': '192.168.220.50',
    'username': 'Samuel',
    'password': 'Samuel@123',
    'port': 22
    },
    {
    'device_type': 'cisco_ios',
    'host': '192.168.220.51',
    'username': 'Samuel',
    'password': 'Samuel@123',
    'port': 22
    },
    {
    'device_type': 'cisco_ios',
    'host': '192.168.220.52',
    'username': 'Samuel',
    'password': 'Samuel@123',
    'port': 22
    },
    {
    'device_type': 'cisco_ios',
    'host': '192.168.220.53',
    'username': 'Samuel',
    'password': 'Samuel@123',
    'port': 22
    },
]

# Iterate through the list to access each device
for device in devices:
    # Error handling
    try:
        print(" [+] Trying to connect to", device['host'])
        # SSH connection
        ssh = ConnectHandler(**device)
        print(" [+] Connected successfully to", device['host'])
        # Enter device enable mode
        ssh.enable()
    except Exception as e:
        print("Ran into some issues:", e)

    # Handle error
    try:
        result = ssh.send_command('show ip int b')
        print(result)
        # Disconnect from SSH device
        ssh.disconnect()
        print(" [-] Disconnected from", device['host'], "successfully!")
    except Exception as e:
        print("Ran into some issues:", e)
    
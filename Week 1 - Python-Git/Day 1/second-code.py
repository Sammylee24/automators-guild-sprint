from netmiko import ConnectHandler

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

for device in devices:
    try:
        print(" [+] Trying to connect to", device['host'])
        ssh = ConnectHandler(**device)
        print(" [+] Connected successfully to", device['host'])
        ssh.enable()
    except Exception as e:
        print("Ran into some issues:", e)

    try:
        result = ssh.send_command('show ip int b')
        print(result)
        ssh.disconnect()
        print(" [-] Disconnected from", device['host'], "successfully!")
    except Exception as e:
        print("Ran into some issues:", e)
    
from netmiko import ConnectHandler
from device_list import devices

for device in devices:
    try:
        print(" [+] Trying to connect to", device['host'])
        ssh = ConnectHandler(**device)
        print(" [+] Connected successfully to", device['host'])
        ssh.enable
    except Exception as e:
        print("Ran into some issues:", e)
    
    try:
        result = ssh.send_command('show ip int b')
        print(result)
    except Exception as e:
        print("Ran into some issues:", e)
        
# Import releveant modules
from netmiko import ConnectHandler
from device_list import devices  # Imported from another python file

# Loop through devices imported as module
for device in devices:
    # Error handling
    try:
        print(" [+] Trying to connect to", device['host'])
        # SSH connection to device
        ssh = ConnectHandler(**device)
        print(" [+] Connected successfully to", device['host'])
        # Enter device enable mode
        ssh.enable()
    except Exception as e:
        print("Ran into some issues:", e)
    
    # Handling errors
    try:
        # Executing command
        result = ssh.send_command('show ip int b')
        print(result)
    except Exception as e:
        print("Ran into some issues:", e)

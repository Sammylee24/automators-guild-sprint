# Import relevant libraries
from netmiko import ConnectHandler

# Function to connect to device
def connect_device(device):
    try:
        print("[+] Trying to connect to", device['host'])
        ssh = ConnectHandler(**device)
        print("[+] Successfully connected to", device['host'])
        return ssh
    except Exception as e:
        print(e)

# Function to enter enable mode
def enable_device(ssh, device):
    try:
        if device['device_type'] == 'cisco_ios':
            print("[+] Navigating to command mode on", device['host'])
            ssh.enable()
            print("[+] Success!")
    except Exception as e:
        print(e)

# Execute command on device
def execute_command(ssh, command):
    try:
        #print("[+] Attempting command execution on", device['host'])
        result = ssh.send_command(command)
        return result
    except Exception as e:
        print(e)
        return None

# Send configuration set to device
def config_device(ssh, config):
    try:
        result = ssh.send_config_set(config)
        return result
    except Exception as e:
        print(e)

# Send config from file
def file_config(ssh, conf):
    try:
        result = ssh.send_config_from_file(conf)
        return result
    except Exception as e:
        print(e)

# Disconnect from device
def device_disconnect(ssh):
    try:
        #print("[-] Tryint to disconnect from", device['host'])
        ssh.disconnect()
        print("[+] Success!")
    except Exception as e:
        print(e)
    
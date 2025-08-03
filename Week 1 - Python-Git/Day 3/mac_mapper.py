# This code logs into a switch and retrieves
# all MAC addresses learnt from all interfaces

import getpass as gt
import netmiko as nt
import re

def get_device_info():
    try:
        ip_pattern = r'\b(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}' \
                     r'(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\b'

        while True:
            device_type = input("Is this a Cisco device? (Enter Y or N): ").strip().upper()
            if device_type == 'Y':
                device_type = 'cisco_ios'
                break
            elif device_type == 'N':
                print("This script currently supports only Cisco devices. Exiting.")
                exit(0)
            else:
                print("Wrong selection. Please enter Y or N.")

        while True:
            device = input("Enter device IP address: ").strip()
            if re.fullmatch(ip_pattern, device):
                break
            else:
                print("Invalid IP address format. Please enter a valid IPv4 address.")

        username = input("Enter Device login username: ").strip()
        password = gt.getpass("Enter device password: ").strip()

        return device_type, device, username, password

    except Exception as e:
        print("[!] Error in device input:", e)

def connect_device(device):
    try:
        print("[+] Trying to connect to", device['host'])
        ssh = nt.ConnectHandler(**device)
        print("[+] Connection successful!")
        return ssh
    except Exception as e:
        print(e)

def enable_device(ssh, device):
    try:
        ssh.enable()
        print("Entered enable mode for", device['host'], "successfully!")
    except Exception as e:
        print(e)

def learn_mac(ssh, command, device):
    try:
        result = ssh.send_command(command)
        print("Fetched MAC addresses from", device['host'], "successfully!")
        return result
    except Exception as e:
        print(e)

def extract_macs_from_device(result):
    extract = []
    count = 0
    try:
        # Regex for MAC address mapping
        mac_pattern = (
        r'\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b'        # aa:bb:cc:dd:ee:ff or aa-bb-cc-dd-ee-ff
        r'|'
        r'\b(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}\b'           # aabb.ccdd.eeff
    )

        mac_addresses = set()   # To avoid duplicates

        for line in result.splitlines():
            matches = re.findall(mac_pattern, line)
            for mac in matches:
                mac_addresses.add(mac)
                count += 1
        extract = sorted(mac_addresses)
        print(count, "uniques MAC addresses found!")
        return extract
    except Exception as e:
        print(e)

def mac_vlan_int(result):
    try:
        print("\nMAC Address Mapping (VLAN | MAC | Interface):")
        print(f"{'VLAN':<6} {'MAC Address':<20} {'Interface':<15}")
        print("-" * 45)

        for line in result.splitlines():
            parts = line.split()
            if len(parts) >= 4:
                vlan = parts[0]
                mac = parts[1]
                interface = parts[-1]

                # Basic MAC validation (skip non-MAC entries)
                if re.match(r'^(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}$|^(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$', mac):
                    print(f"{vlan:<6} {mac:<20} {interface:<15}")

    except Exception as e:
        print("[!] Error parsing MAC table:", e)

def disconnect_device(ssh, device):
    try:
        ssh.disconnect()
        print("Disconnected from", device['host'])
    except Exception as e:
        print(e)

device_type, device_ip, username, password = get_device_info()

device = {
    'device_type': device_type,
    'host': device_ip,
    'username': username,
    'password': password,
    'port': 22
}

connection = connect_device(device)
enable_device(connection, device)
macs = learn_mac(connection, 'show mac address-table', device)
extracted_macs = extract_macs_from_device(macs)
print(extracted_macs)
mac_vlan_int(macs)
disconnect_device(connection, device)

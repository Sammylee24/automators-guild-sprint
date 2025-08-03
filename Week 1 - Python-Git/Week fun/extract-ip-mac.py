import getpass
import netmiko
import re
import sys

def get_device_info():
    try:
        ip_pattern = re.compile(
            r'\b(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}'
            r'(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\b'
        )

        while True:
            device_choice = input("Is this a Cisco device? (Enter Y or N): ").strip().upper()
            if device_choice == 'Y':
                device_type = 'cisco_ios'
                break
            elif device_choice == 'N':
                print("This script currently supports only Cisco devices. Exiting.")
                sys.exit(0)
            else:
                print("Invalid input. Please enter Y or N.")

        while True:
            ip = input("Enter device IP address: ").strip()
            if ip_pattern.fullmatch(ip):
                break
            else:
                print("Invalid IPv4 address. Please try again.")

        username = input("Enter device login username: ").strip()
        password = getpass.getpass("Enter device password: ").strip()

        return {
            'device_type': device_type,
            'host': ip,
            'username': username,
            'password': password,
            'port': 22
        }

    except Exception as e:
        print("[!] Error in device input:", e)
        sys.exit(1)

def connect_device(device):
    try:
        print(f"[+] Connecting to {device['host']} ...")
        ssh = netmiko.ConnectHandler(**device)
        print("[+] Connection successful!")
        return ssh
    except Exception as e:
        print(f"[!] Connection failed: {e}")
        sys.exit(1)

def enable_device(ssh, host):
    try:
        ssh.enable()
        print(f"[+] Enable mode entered on {host}")
    except Exception as e:
        print(f"[!] Enable mode failed: {e}")
        ssh.disconnect()
        sys.exit(1)

def get_mac_table(ssh, command, host):
    try:
        output = ssh.send_command(command)
        print(f"[+] MAC address table fetched from {host}")
        return output
    except Exception as e:
        print(f"[!] Failed to retrieve MAC table: {e}")
        ssh.disconnect()
        sys.exit(1)

def extract_unique_macs(text):
    try:
        mac_pattern = re.compile(
            r'(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}'
            r'|(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}'
        )
        mac_set = set()
        total = 0

        for line in text.splitlines():
            matches = mac_pattern.findall(line)
            total += len(matches)
            mac_set.update(matches)

        print(f"[+] Retrieved {total} MAC entries, {len(mac_set)} unique.\n")
        return sorted(mac_set)
    except Exception as e:
        print(f"[!] MAC extraction error: {e}")
        return []

def print_mac_vlan_interface_table(mac_output):
    try:
        mac_format = re.compile(
            r'^(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}$|^(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$'
        )

        print("\nMAC Address Mapping (VLAN | MAC | Interface):")
        print(f"{'VLAN':<6} {'MAC Address':<20} {'Interface':<15}")
        print("-" * 45)

        for line in mac_output.splitlines():
            parts = line.split()
            if len(parts) >= 4:
                vlan, mac, _, interface = parts[:4]
                if mac_format.match(mac):
                    print(f"{vlan:<6} {mac:<20} {interface:<15}")
    except Exception as e:
        print("[!] Error parsing MAC table:", e)

def disconnect_device(ssh, host):
    try:
        ssh.disconnect()
        print(f"[+] Disconnected from {host}")
    except Exception as e:
        print(f"[!] Error during disconnect: {e}")

def main():
    device = get_device_info()
    ssh = connect_device(device)
    enable_device(ssh, device['host'])
    mac_output = get_mac_table(ssh, 'show mac address-table', device['host'])
    mac_list = extract_unique_macs(mac_output)
    if mac_list:
        print("[+] Unique MACs:")
        for mac in mac_list:
            print(mac)
    print_mac_vlan_interface_table(mac_output)
    disconnect_device(ssh, device['host'])

if __name__ == '__main__':
    main()

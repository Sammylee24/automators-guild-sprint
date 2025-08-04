import getpass
import netmiko
import re
import sys
import argparse

MAC_PATTERN = re.compile(
    r'(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}'
    r'|(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}'
)

def connect_device(device):
    try:
        ssh = netmiko.ConnectHandler(**device)
        return ssh
    except Exception:
        return None

def enable_device(ssh, host):
    try:
        ssh.enable()
    except Exception:
        ssh.disconnect()
        sys.exit(1)

def get_hostname(ssh):
    try:
        output = ssh.send_command("show run | include hostname")
        if output.lower().startswith("hostname"):
            return output.split()[1]
        return "Unknown"
    except Exception:
        return "Unknown"

def get_mac_table(ssh, command, host):
    try:
        return ssh.send_command(command)
    except Exception:
        ssh.disconnect()
        sys.exit(1)

def extract_unique_macs(text):
    try:
        mac_set = set()
        for line in text.splitlines():
            matches = MAC_PATTERN.findall(line)
            mac_set.update(matches)
        return sorted(mac_set)
    except Exception:
        return []

def disconnect_device(ssh, host):
    try:
        ssh.disconnect()
    except Exception:
        pass

def search_mac():
    try:
        parser = argparse.ArgumentParser(description="Search for a MAC address.")
        parser.add_argument('--search', type=str, help='Enter MAC address to search (optional)')
        args = parser.parse_args()
        return args.search.strip() if args.search else None
    except Exception:
        sys.exit(1)

def normalize_mac(mac):
    return mac.replace(":", "").replace("-", "").replace(".", "").lower()

def parse_mac_table(mac_output, host, hostname):
    results = []
    for line in mac_output.splitlines():
        parts = line.split()
        if len(parts) >= 4:
            vlan, mac, _, interface = parts[:4]
            if MAC_PATTERN.match(mac):
                results.append({
                    "hostname": hostname,
                    "device": host,
                    "vlan": vlan,
                    "mac": mac,
                    "interface": interface
                })
    return results

def display_results(all_mac_entries, search_mac=None):
    if search_mac:
        search_mac_normalized = normalize_mac(search_mac)
        found_entries = [
            entry for entry in all_mac_entries
            if normalize_mac(entry["mac"]) == search_mac_normalized
        ]

        if found_entries:
            print(f"\nMAC '{search_mac}' found on:")
            print(f"{'Hostname':<15} {'IP':<15} {'VLAN':<6} {'MAC':<20} {'Interface':<15}")
            print("-" * 75)
            for entry in found_entries:
                print(f"{entry['hostname']:<15} {entry['device']:<15} {entry['vlan']:<6} {entry['mac']:<20} {entry['interface']:<15}")
        else:
            print(f"\n[!] MAC '{search_mac}' not found on any device.")
            print("\nAll Found MACs:")
            print(f"{'Hostname':<15} {'IP':<15} {'VLAN':<6} {'MAC':<20} {'Interface':<15}")
            print("-" * 75)
            for entry in all_mac_entries:
                print(f"{entry['hostname']:<15} {entry['device']:<15} {entry['vlan']:<6} {entry['mac']:<20} {entry['interface']:<15}")
    else:
        print("\nMAC Address Mapping (All Devices):")
        print(f"{'Hostname':<15} {'IP':<15} {'VLAN':<6} {'MAC':<20} {'Interface':<15}")
        print("-" * 75)
        for entry in all_mac_entries:
            print(f"{entry['hostname']:<15} {entry['device']:<15} {entry['vlan']:<6} {entry['mac']:<20} {entry['interface']:<15}")

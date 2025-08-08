# network_util.py (New, Multi-Vendor Version)

import re
import sys
import argparse
import netmiko

# --- Constants and Patterns ---
MAC_PATTERN = re.compile(
    r'(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}'   # Regular MAC format
    r'|(?:[0-9A-Fa-f]{4}[.-]){2}[0-9A-Fa-f]{4}' # Cisco/Huawei format
)

# --- Vendor-Specific Command Mapping ---
COMMANDS = {
    'cisco_ios': {
        'mac_table': 'show mac address-table',
        'hostname': 'show run | include hostname'
    },
    'huawei_vrp': {
        'mac_table': 'display mac-address',
        'hostname': 'display current-configuration | include sysname'
    },
    # Other vendors here later
}

# --- Connection and Execution Functions ---

def connect_device(device):
    try:
        return netmiko.ConnectHandler(**device)
    except Exception as e:
        print(f"[!] Error connecting to {device.get('host')}: {e}")
        return None

def enable_device(ssh):
    try:
        if ssh.check_enable_mode():
            return True
        ssh.enable()
        return True
    except Exception as e:
        print(f"[!] FAILED to enter enable mode on {ssh.host}: {e}")
        return False

def get_hostname(ssh, device):
    device_type = device.get('device_type', 'unknown')
    command = COMMANDS.get(device_type, {}).get('hostname')

    if not command:
        return "Unknown_Vendor"
        
    try:
        output = ssh.send_command(command)
        if 'hostname' in command: # Cisco
            return output.split()[1]
        elif 'sysname' in command: # Huawei
            return output.split()[1]
    except Exception:
        pass
    return "Unknown_Host"

def get_mac_table(ssh, device):
    device_type = device.get('device_type', 'unknown')
    command = COMMANDS.get(device_type, {}).get('mac_table')

    if not command:
        print(f"[!] MAC table command not defined for device_type: {device_type}")
        return None
        
    try:
        return ssh.send_command(command)
    except Exception as e:
        print(f"[!] Failed to get MAC table from {ssh.host}: {e}")
        return None

def disconnect_device(ssh):
    try:
        ssh.disconnect()
    except Exception:
        pass

# --- Data Parsing and Normalization ---

def normalize_mac(mac):
    return mac.replace(":", "").replace("-", "").replace(".", "").lower()

def _parse_cisco_mac_table(mac_output):
    """Parses the output of 'show mac address-table'."""
    parsed_entries = []
    # Skip header lines, find the start of the data
    lines = mac_output.strip().splitlines()
    data_started = False
    for line in lines:
        if '----' in line: # Common delimiter before data starts
            data_started = True
            continue
        if not data_started:
            continue
            
        parts = line.split()
        if len(parts) >= 4 and MAC_PATTERN.match(parts[1]):
            vlan, mac, mac_type, interface = parts[0], parts[1], parts[2], ' '.join(parts[3:])
            parsed_entries.append({'vlan': vlan, 'mac': mac, 'interface': interface})
    return parsed_entries

def _parse_huawei_mac_table(mac_output):
    """Parses the output of 'display mac-address'."""
    parsed_entries = []
    # Skip header lines, find the start of the data
    lines = mac_output.strip().splitlines()
    data_started = False
    for line in lines:
        if '----' in line:
            data_started = True
            continue
        if not data_started:
            continue
            
        parts = line.split()
        # Huawei format: MAC, VLAN/VSI/BD, Learned-From, Type
        if len(parts) >= 4 and MAC_PATTERN.match(parts[0]):
            mac, vlan_info, interface = parts[0], parts[1], parts[2]
            # Extract VLAN from 'VLAN/VSI/BD' column if possible
            vlan = vlan_info.split('/')[0] if '/' in vlan_info else vlan_info
            parsed_entries.append({'vlan': vlan, 'mac': mac, 'interface': interface})
    return parsed_entries

# --- Main Parser Dispatcher ---
# This is the key to scalability. It looks up the correct parser function to use.
PARSERS = {
    'cisco_ios': _parse_cisco_mac_table,
    'huawei_vrp': _parse_huawei_mac_table,
    # Other vendor parsers here later
}

def parse_mac_table(mac_output, device_type):
    """
    Dispatcher function that calls the correct vendor-specific parser.
    """
    parser_func = PARSERS.get(device_type)
    if parser_func:
        return parser_func(mac_output)
    else:
        print(f"[!] No parser available for device_type: {device_type}")
        return []

# --- CLI and Display Functions ---

def get_cli_args():
    parser = argparse.ArgumentParser(description="Search for a MAC address across multiple network devices.")
    parser.add_argument('--search', type=str, help='Enter MAC address to search for (optional)')
    args = parser.parse_args()
    return args.search.strip() if args.search else None

def display_results(all_mac_entries, search_mac=None):
    # This function remains largely the same, as it works with the standardized dictionary format.
    print_header = f"{'Hostname':<20} {'Device IP':<18} {'VLAN':<8} {'MAC Address':<20} {'Interface'}"
    print_divider = "-" * len(print_header)

    if search_mac:
        search_mac_normalized = normalize_mac(search_mac)
        found_entries = [
            entry for entry in all_mac_entries
            if normalize_mac(entry["mac"]) == search_mac_normalized
        ]
        if found_entries:
            print(f"\n✅ MAC '{search_mac}' found on:")
            print(print_header)
            print(print_divider)
            for entry in found_entries:
                print(f"{entry['hostname']:<20} {entry['device_ip']:<18} {entry['vlan']:<8} {entry['mac']:<20} {entry['interface']}")
        else:
            print(f"\n[!] MAC '{search_mac}' not found on any device.")
    else:
        print("\nMAC Address Mapping (All Devices):")
        print(print_header)
        print(print_divider)
        for entry in all_mac_entries:
            print(f"{entry['hostname']:<20} {entry['device_ip']:<18} {entry['vlan']:<8} {entry['mac']:<20} {entry['interface']}")

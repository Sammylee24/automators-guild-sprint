import re
import sys

def extract_ips_from_log(file_path):
    try:
        # Strict IPv4 regex — ensures octets are 0–255
        ip_pattern = r'\b(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)' \
                    r'\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\b'

        ip_addresses = set()    # To avoid duplicates
        total_ip_count = 0

        with open(file_path, 'r') as file:
            for line in file:
                matches = re.findall(ip_pattern, line)
                total_ip_count += len(matches)
                ip_addresses.update(matches)
        unique_ip_count = len(ip_addresses)
        print(f"\nRetrieved {total_ip_count} IP addresses, {unique_ip_count} are unique.\n")
        return sorted(ip_addresses)
    except Exception as e:
        print(e)
        sys.exit(1)

def extract_macs_from_log(file_path):
    try:
        # Regex for MAC address mapping
        mac_pattern = (
        r'\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b'        # aa:bb:cc:dd:ee:ff or aa-bb-cc-dd-ee-ff
        r'|'
        r'\b(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}\b'           # aabb.ccdd.eeff
    )

        mac_addresses = set()   # To avoid duplicates
        total_mac_count = 0

        with open(file_path, 'r') as file:
            for line in file:
                matches = re.findall(mac_pattern, line)
                total_mac_count += len(matches)
                mac_addresses.update(matches)
        unique_mac_count = len(mac_addresses)
        print(f"\nRetrieved {total_mac_count} MAC addresses, {unique_mac_count} are unique.\n")
        return sorted(mac_addresses)
    except Exception as e:
        print(e)
        sys.exit(1)

def main():
    log_file = 'log.txt'
    ips = extract_ips_from_log(log_file)
    macs = extract_macs_from_log(log_file)
    
    print("Found IP addresses:")
    for ip in ips:
        print(ip)

    print("\n\n\nFound MAC addresses:")
    for mac in macs:
        print(mac)
        
if __name__ == '__main__':
    main()

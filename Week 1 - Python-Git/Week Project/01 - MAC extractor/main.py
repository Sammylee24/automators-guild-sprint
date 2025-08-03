import re
import argparse
import sys
import os

def parse_file():
    try:
        parser = argparse.ArgumentParser(description="Process a file input.")
        parser.add_argument('--file', type=str, required=True, help='Path to the input file')
        args = parser.parse_args()
        return args.file
    except Exception as e:
        print("[!] Error parsing arguments:", e)
        sys.exit(1)

def extract_macs_from_log(file_path):
    try:
        mac_pattern = re.compile(
            r'\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b'
            r'|'
            r'\b(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}\b'
        )

        mac_addresses = set()
        total_count = 0

        if not os.path.isfile(file_path):
            print(f"[!] File does not exist: {file_path}")
            sys.exit(1)

        with open(file_path, 'r') as file:
            for line in file:
                matches = mac_pattern.findall(line)
                total_count += len(matches)
                mac_addresses.update(matches)
        unique_count = len(mac_addresses)
        print(f"\nRetrieved {total_count} MAC addresses, {unique_count} are unique.\n")
        return sorted(mac_addresses)

    except Exception as e:
        print("[!] Error reading file:", e)
        return []
        sys.exit(1)

def normalize_mac(mac):
    try:
        mac = mac.replace('-', '').replace(':', '').replace('.', '')
        return ':'.join(mac[i:i+2] for i in range(0, 12, 2)).lower()
    except Exception as e:
        print("[!] Error normalizing MACs", e)
        sys.exit(1)

def main():
    log_file = parse_file()
    macs = extract_macs_from_log(log_file)
    normalized_macs = set(normalize_mac(m) for m in macs)

    if normalized_macs:
        print("MAC Addresses Found:")
        for mac in normalized_macs:
            print(mac)

if __name__ == '__main__':
    main()

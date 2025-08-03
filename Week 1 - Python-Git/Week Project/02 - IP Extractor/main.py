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

def extract_ips_from_log(file_path):
    try:
        # Strict IPv4 regex — ensures octets are 0–255
        ip_pattern = r'\b(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)' \
                    r'\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\b'

        ip_addresses = set()    # To avoid duplicates
        total_count = 0

        if not os.path.isfile(file_path):
            print(f"[!] File does not exist: {file_path}")
            sys.exit(1)

        with open(file_path, 'r') as file:
            for line in file:
                matches = re.findall(ip_pattern, line)
                total_count += len(matches)
                ip_addresses.update(matches)
        unique_count = len(ip_addresses)
        print(f"\nRetrieved {total_count} IP addresses, {unique_count} are unique.\n")
        return sorted(ip_addresses)
    except Exception as e:
        print("[!] Error reading file:", e)
        return []
        sys.exit(1)

def main():
    log_file = parse_file()
    ips = extract_ips_from_log(log_file)

    if ips:
        for ip in ips:
            print(ip)

if __name__ == '__main__':
    main()

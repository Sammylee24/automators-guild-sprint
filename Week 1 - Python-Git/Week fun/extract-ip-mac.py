import re

def extract_ips_from_log(file_path):
    # Strict IPv4 regex — ensures octets are 0–255
    ip_pattern = r'\b(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)' \
                 r'\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\b'

    ip_addresses = set()    # To avoid duplicates

    with open(file_path, 'r') as file:
        for line in file:
            matches = re.findall(ip_pattern, line)
            for ip in matches:
                ip_addresses.add(ip)

    return sorted(ip_addresses)

def extract_macs_from_log(file_path):
    # Regex for MAC address mapping
    mac_pattern = (
    r'\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b'        # aa:bb:cc:dd:ee:ff or aa-bb-cc-dd-ee-ff
    r'|'
    r'\b(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}\b'           # aabb.ccdd.eeff
)


    mac_addresses = set()   # To avoid duplicates

    with open(file_path, 'r') as file:
        for line in file:
            matches = re.findall(mac_pattern, line)
            for mac in matches:
                mac_addresses.add(mac)
    return sorted(mac_addresses)

# Usage
log_file = 'log.txt'
ips = extract_ips_from_log(log_file)
macs = extract_macs_from_log(log_file)
ip_count = 0
mac_count = 0

print("Found IP addresses:")
for ip in ips:
    print(ip)
    ip_count += 1
print("A total of", ip_count, "IP addresses were found.")

print("\n\n\nFound MAC addresses:")
for mac in macs:
    print(mac)
    mac_count += 1
print("A total of", mac_count, "MAC addresses were found.")

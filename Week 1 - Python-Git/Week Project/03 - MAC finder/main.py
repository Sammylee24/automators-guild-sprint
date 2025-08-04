import network_util as nu
from hosts import devices
from tqdm import tqdm

def main():
    mac_to_find = nu.search_mac()
    all_mac_entries = []
    seen_ips = set()

    for device in tqdm(devices, desc="Processing devices", unit="device"):
        ip = device['host']
        if ip in seen_ips:
            continue  # Skip duplicates
        seen_ips.add(ip)

        ssh = nu.connect_device(device)
        if not ssh:
            continue

        nu.enable_device(ssh, ip)
        hostname = nu.get_hostname(ssh)
        mac_output = nu.get_mac_table(ssh, 'show mac address-table', ip)
        entries = nu.parse_mac_table(mac_output, ip, hostname)
        all_mac_entries.extend(entries)
        nu.disconnect_device(ssh, ip)

    nu.display_results(all_mac_entries, search_mac=mac_to_find)

if __name__ == '__main__':
    main()

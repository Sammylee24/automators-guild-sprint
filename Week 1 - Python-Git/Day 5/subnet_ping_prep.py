import sys
import ipaddress
import platform
import subprocess
import concurrent.futures
from tqdm import tqdm

def ping_host(ip_address):
    """
    Pings a single IP address using subprocess and PARSES THE OUTPUT for success.
    This is the most reliable method for Windows environments.
    """
    ip_str = str(ip_address)
    
    if platform.system().lower() == 'windows':
        command = ['ping', '-n', '1', '-w', '1000', ip_str]
    else:
        command = ['ping', '-c', '1', '-W', '1', ip_str]

    try:
        output = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5
        ).stdout.lower()

        if "bytes=" in output and "ttl=" in output:
            return ip_str
        else:
            return None
            
    except (subprocess.TimeoutExpired, Exception):
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python final_pinger.py <NETWORK_CIDR>")
        print("Example: python final_pinger.py 192.168.1.0/29")
        sys.exit(1)

    network_cidr = sys.argv[1]

    try:
        network = ipaddress.ip_network(network_cidr, strict=False)
        hosts_to_ping = list(network.hosts())
        
        if not hosts_to_ping:
            print(f"[!] The network {network_cidr} has no usable host addresses.")
            sys.exit(0)

        # The print statement is now removed from here to keep the console clean for tqdm

    except ValueError as e:
        print(f"[!] Error: Invalid network address provided. {e}")
        sys.exit(1)

    online_hosts = []
    
    # 2. Wrap the executor.map() call with tqdm()
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        # Create a tqdm progress bar
        # total=len(hosts_to_ping) tells tqdm the size of the task
        # desc="..." sets the description text
        pbar = tqdm(total=len(hosts_to_ping), desc="Pinging hosts", unit="host")
        
        # We use as_completed to update the progress bar as each task finishes
        future_to_ip = {executor.submit(ping_host, ip): ip for ip in hosts_to_ping}
        
        for future in concurrent.futures.as_completed(future_to_ip):
            result = future.result()
            if result:
                online_hosts.append(result)
            pbar.update(1) # Update the progress bar by 1 for each completed future
        pbar.close() # Close the progress bar when done

    print("\n--- Scan Complete ---")
    if online_hosts:
        print(f"✅ The following {len(online_hosts)} hosts are online:")
        for host in sorted(online_hosts, key=ipaddress.ip_address):
            print(f"  - {host}")
    else:
        print("❌ No hosts responded to ping.")

if __name__ == '__main__':
    main()
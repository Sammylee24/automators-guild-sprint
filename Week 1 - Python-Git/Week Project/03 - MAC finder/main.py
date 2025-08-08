# main.py (The Threaded Version)

import network_util as nu
from hosts import devices
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

def process_device(device):
    """
    This function contains the entire workflow for ONE device.
    It's the "job" that we will give to each of our worker threads.
    It returns a list of dictionary entries for the MACs found on this device.
    """
    ip = device.get('host')
    device_type = device.get('device_type')
    
    ssh = nu.connect_device(device)
    if not ssh:
        return []

    if not nu.enable_device(ssh):
        nu.disconnect_device(ssh)
        return []

    hostname = nu.get_hostname(ssh, device)
    mac_output = nu.get_mac_table(ssh, device)
    
    nu.disconnect_device(ssh)

    if not mac_output:
        return []

    parsed_entries = nu.parse_mac_table(mac_output, device_type)

    final_entries = []
    for entry in parsed_entries:
        final_entries.append({
            "hostname": hostname,
            "device_ip": ip,
            "vlan": entry.get('vlan', '-'),
            "mac": entry.get('mac', '-'),
            "interface": entry.get('interface', '-')
        })
    return final_entries

def main():
    start_time = datetime.now()
    mac_to_find = nu.get_cli_args()
    all_mac_entries = []

    # --- THIS IS THE THREADING IMPLEMENTATION ---

    # 1. We create a ThreadPoolExecutor. This is our pool of worker threads.
    #    'max_workers=5' means we will run up to 5 device connections at the same time.
    #    The 'with' statement ensures the pool is cleaned up properly when we're done.
    with ThreadPoolExecutor(max_workers=5) as executor:
        
        # 2. We submit our jobs to the pool.
        #    executor.submit(process_device, device) tells a thread to run our function
        #    with the 'device' dictionary as its argument.
        #    We create a dictionary mapping each 'future' (a running task) back to the device
        #    it belongs to. This helps us track which task is which.
        future_to_device = {executor.submit(process_device, device): device for device in devices}
        
        # 3. We create a tqdm progress bar.
        #    as_completed(future_to_device) is a powerful function. It doesn't wait for all
        #    threads to finish. It gives us back each 'future' as soon as it completes.
        #    This is what allows our progress bar to update in real-time.
        pbar = tqdm(as_completed(future_to_device), total=len(devices), desc="Querying Devices")
        
        # 4. We loop through the completed futures.
        for future in pbar:
            device = future_to_device[future] # Get the device associated with this completed task.
            try:
                # 5. We get the result from the thread. future.result() returns whatever
                #    our process_device function returned (the list of MAC entries).
                result_entries = future.result()
                if result_entries:
                    all_mac_entries.extend(result_entries)
            except Exception as e:
                # If a thread had an unexpected error, we can catch it here.
                # pbar.write() prints a message without messing up the progress bar.
                pbar.write(f"[!] Error processing device {device.get('host')}: {e}")

    # --- END OF THREADING IMPLEMENTATION ---

    nu.display_results(all_mac_entries, search_mac=mac_to_find)
    
    end_time = datetime.now()
    print(f"\nTotal script run time: {end_time - start_time}")

if __name__ == '__main__':
    main()

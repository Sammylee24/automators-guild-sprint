from concurrent.futures import ThreadPoolExecutor
from hosts import devices
from netmiko import ConnectHandler

def task(device):
    print(f"Connecting to {device['host']}...")
    ssh = ConnectHandler(**device)
    ssh.enable()
    tasking = ssh.send_command("show mac add")
    print(tasking)
    ssh.disconnect()

with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(task, devices)

print("All done.")

# import relevant modules
import yaml
from netmiko import ConnectHandler
import os
import difflib
import shutil
from datetime import datetime
import subprocess
import re
from functools import wraps
import traceback

def safe_run(default_return=None):
    """
    Decorator to catch and print exceptions for a function,
    then return a default value.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"[ERROR] {func.__name__}: {e}")
                traceback.print_exc()
                return default_return
        return wrapper
    return decorator

@safe_run(default_return=(None, None, None))
def get_device_config(device):
    """
    This connects to device and return
    the running configuration
    """
    # Vendor-Specific Command Mapping
    COMMANDS = {
        'cisco_ios': {
            'running_config': 'show running-config',
            'hostname': 'show running-config | include hostname',
            'to_find': 'hostname'
        },
        'huawei_vrp': {
            'running_config': 'display current-configuration',
            'hostname': 'display current-configuration | include sysname',
            'to_find': 'sysname'
        },
        'juniper_junos': {
            'running_config': 'show configuration',
            'hostname': 'show configuration | match host-name',
            'to_find': 'host-name'
        },
        'mikrotik_routeros': {
            'running_config': '/export'
        }
        # Other vendors here later
    }
    # Connect to device
    ssh = ConnectHandler(**device)
    print(f"Connected to {device['host']}")
    if device['device_type'] == 'cisco_ios':
        # Enable for Cisco devices
        ssh.enable()
    
    # Get running-configuration
    device_type = device.get('device_type', 'unknown')
    run_cmd = COMMANDS.get(device_type, {}).get('running_config')
    running_config = ssh.send_command(run_cmd)
    # Extract device hostname
    if device_type != 'mikrotik_routeros':
        raw_hostname = ssh.send_command(COMMANDS.get(device_type, {}).get('hostname'))
        to_find = COMMANDS.get(device_type, {}).get('to_find')
        hostname = raw_hostname.replace(to_find, "").strip().replace(";", "").strip()
    else:
        raw_value = f"[{device['username']}@"
        hostname = ssh.find_prompt().replace("] >", "").strip().replace(raw_value, "").strip()
    return (hostname, running_config, ssh)

@safe_run(default_return=(None, None, None))
def save_temp_config(hostname, running_config):
    """
    Saves configuration temporarily to /temp and
    returns the path
    """
    # Set filename and directory
    config_file = f"configs/{hostname}.cfg"
    # Create a timestamp for the temp file (YYYYMMDD-HHMMSS)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    temp_file = f"temp/{hostname}_{timestamp}.cfg"

    # Save running-config to file
    with open(temp_file, 'w') as f:
        f.write(running_config)
    print(f"Saved running-config temporarily to {temp_file}")
    return (temp_file, config_file, timestamp)

@safe_run()
def update_and_commit(config_file, temp_file, hostname, timestamp):
    # Handle diff, copy, and git commit
    if os.path.exists(config_file):
        diff_output = compare_configs(config_file, temp_file)
        if diff_output:
            print("CHANGE DETECTED!")
            print(diff_output)
            shutil.copy(temp_file, config_file)
            print(f"Updated {config_file} for {hostname}")
            
            # Commit changes to git
            commit_changes(config_file, hostname, timestamp)
        else:
            print("No changes detected")
    else:
        # First time: just save directly
        shutil.copy(temp_file, config_file)
        print(f"First run – saved initial backup to {config_file}")

@safe_run(default_return=[])
def clean_config_lines(lines):
    """
    Remove volatile lines from configs (Cisco, Mikrotik, Juniper…)
    so diffs only show real changes.
    """
    NOISE_PATTERNS = [
        r"^Current configuration.*bytes",
        r"^! Last configuration change.*",
        r"^! NVRAM config last updated.*",
        r"^Building configuration",
        r"^# \w{3}/\d{2}/\d{4}",          # Mikrotik timestamp
        r"^## Last commit:.*"             # Juniper commit timestamp
    ]
    return [
        l for l in lines
        if not any(re.match(p, l) for p in NOISE_PATTERNS)
    ]

@safe_run(default_return='')
def compare_configs(old_file, new_file):
    """
    Compare two configuration files and return their diff output.
    :param old_file: Path to the old config file
    :param new_file: Path to the new config file
    :return: String containing the unified diff
    """
    # Read old file
    with open(old_file, 'r') as f:
        old_lines = f.readlines()
    
    # Read new file
    with open(new_file, 'r') as f:
        new_lines = f.readlines()

    old_clean = clean_config_lines(old_lines)
    new_clean = clean_config_lines(new_lines)

    # Generate unified diff
    diff = difflib.unified_diff(
        old_clean,
        new_clean,
        fromfile=old_file,
        tofile=new_file,
        lineterm=''  # avoid extra newlines
    )

    # Join into one string
    return '\n'.join(diff)

@safe_run() 
def commit_changes(filename, hostname, detect_time):
    """
    Stage and commit a file to Git with a message containing the hostname.
    :param filename: Path to the file to commit
    :param hostname: Device hostname to include in commit message
    """
    # Stage the file
    subprocess.run(["git", "add", filename], check=True)
    # Commit with a custom message
    commit_message = f"Config change detected on {hostname} at {detect_time}"
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    print(f"Committed {filename} to git with message: '{commit_message}'")

@safe_run()
def disconnect_device(ssh):
    # Disconnect from device
    ssh.disconnect()
    
def main():
    # Create the directories if they do not exist
    os.makedirs("configs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)

    with open('hosts.yaml', 'r') as file:
        # Convert YAML to Python dictionary
        data = yaml.safe_load(file)

    for device in data['devices']:
        hostname, running_config, ssh = get_device_config(device)
        if hostname and running_config:
            temp_file, config_file, timestamp = save_temp_config(hostname, running_config)
            update_and_commit(config_file, temp_file, hostname, timestamp)
            disconnect_device(ssh)
        else:
            print(f"Skipping {device['host']} because connection/config failed")

if __name__ == "__main__":
    main()
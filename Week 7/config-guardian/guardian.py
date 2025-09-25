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
import logging
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from threading import Lock
import argparse

# Create one global lock
git_lock = Lock()

# Constants definition
CONFIG_DIR = "configs"
TEMP_DIR = "temp"
LOGS_DIR = "logs"
INVENTORY_DIR = "inventory"
DATE_FORMAT = "%Y%m%d-%H%M%S"

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

def safe_run(default_return=None):
    """
    Decorator to catch and log exceptions for a function,
    then return a default value.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # logs stacktrace automatically
                logger.exception(f"[%s] error", func.__name__)
                return default_return
        return wrapper
    return decorator

class TqdmLoggingHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)  # writes above the progress bar
            self.flush()
        except Exception:
            self.handleError(record)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Config guardian — backup device configs and commit changes to git."
    )
    parser.add_argument(
        "-i", "--inventory",
        default=f"{INVENTORY_DIR}/hosts.yaml",
        help="Path to inventory YAML file (default: inventory/hosts.yaml)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose console logging (DEBUG)."
    )
    return parser.parse_args()

def setup_logger(
    name="config_guardian",
    log_file=f"{LOGS_DIR}/config_guardian_{datetime.now().strftime(DATE_FORMAT)}.log",
    file_level=logging.DEBUG,        # log file level (captures everything)
    console_level=logging.INFO,      # console level (default INFO)
    max_bytes=5_000_000,
    backup_count=5
):
    logger = logging.getLogger(name)

    # ensure logger root level allows handlers to filter
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")

        # rotating file handler (captures file_level and above)
        fh = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        fh.setFormatter(fmt)
        fh.setLevel(file_level)
        logger.addHandler(fh)

        # console handler replaced with tqdm-safe handler
        ch = TqdmLoggingHandler()
        ch.setFormatter(fmt)
        ch.setLevel(console_level)
        logger.addHandler(ch)

    logger.info("\nLog file is saving to %s\n", log_file)
    return logger

@safe_run(default_return=(None, None, None))
def get_device_config(device):
    """
    Connect to a device and return (hostname, running_config, ssh_connection).
    Handles banners and long outputs gracefully.
    """
    # Increase delay factor to handle slow/long-running commands
    ssh = ConnectHandler(**device, global_delay_factor=2)
    logger.info("Connected to %s", device['host'])

    # Cisco needs enable
    if device['device_type'] == 'cisco_ios':
        ssh.enable()

    # Determine commands for this vendor
    device_type = device.get('device_type', 'unknown')
    run_cmd = COMMANDS.get(device_type, {}).get('running_config')

    # Safely run the main config command with longer timeout
    running_config = ssh.send_command(run_cmd, read_timeout=60)

    # Hostname extraction
    if device_type != 'mikrotik_routeros':
        host_cmd = COMMANDS.get(device_type, {}).get('hostname')
        to_find = COMMANDS.get(device_type, {}).get('to_find')

        raw_hostname = ssh.send_command(host_cmd)

        # Pick only the line containing the keyword
        lines = [l for l in raw_hostname.splitlines() if to_find in l]
        if lines:
            clean_line = lines[-1]  # Last matching line usually has the real name
            # Try regex first
            match = re.search(rf"{to_find}\s+(\S+)", clean_line)
            if match:
                hostname = match.group(1)
            else:
                hostname = clean_line.replace(to_find, "").strip().replace(";", "")
        else:
            # Fallback to IP/host if we didn't match anything
            hostname = device['host']
    else:
        # Mikrotik prompt looks like: [user@hostname] >
        raw_value = f"[{device['username']}@"
        prompt = ssh.find_prompt()
        hostname = (
            prompt.replace("] >", "").strip().replace(raw_value, "").strip()
        )

    return (hostname, running_config, ssh)

@safe_run(default_return=(None, None, None))
def save_temp_config(hostname, running_config):
    """
    Saves configuration temporarily to /temp and
    returns the path
    """
    # Set filename and directory
    config_file = f"{CONFIG_DIR}/{hostname}.cfg"
    # Create a timestamp for the temp file (YYYYMMDD-HHMMSS)
    timestamp = datetime.now().strftime(DATE_FORMAT)
    temp_file = f"{TEMP_DIR}/{hostname}_{timestamp}.cfg"

    # Save running-config to file
    with open(temp_file, 'w') as f:
        f.write(running_config)
    logger.info("Saved running-config temporarily to %s", temp_file)
    return (temp_file, config_file, timestamp)

@safe_run()
def update_and_commit(config_file, temp_file, hostname, timestamp):
    # Handle diff, copy, and git commit
    if os.path.exists(config_file):
        diff_output = compare_configs(config_file, temp_file)
        if diff_output:
            logger.warning("CHANGE DETECTED for %s", hostname)
            logger.debug("\n%s", diff_output)
            shutil.copy(temp_file, config_file)
            logger.info(f"Updated {config_file} for {hostname}")
            
            # Commit changes to git
            commit_changes(config_file, hostname, timestamp)
        else:
            logger.info("No changes detected")
    else:
        # First time: just save directly
        shutil.copy(temp_file, config_file)
        logger.info(f"First run – saved initial backup to {config_file}")

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
    # only one thread in here at a time to avoid git index lock
    with git_lock:
        subprocess.run(["git", "add", filename], check=True)
        commit_message = f"Config change detected on {hostname} at {detect_time}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        logger.info(f"Committed {filename} to git with message: '{commit_message}'")

@safe_run()
def disconnect_device(ssh):
    # Disconnect from device
    ssh.disconnect()

def process_device(device):
    hostname, running_config, ssh = get_device_config(device)
    if hostname and running_config:
        temp_file, config_file, timestamp = save_temp_config(hostname, running_config)
        update_and_commit(config_file, temp_file, hostname, timestamp)
        disconnect_device(ssh)
    else:
        logger.info(f"Skipping {device['host']} because connection/config failed")
    
def main(inventory_path):
    # Create the directories if they do not exist
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    with open(inventory_path, 'r') as file:
        # Convert YAML to Python dictionary
        data = yaml.safe_load(file)
    
    devices = data['devices']

    """
    Run devices in parallel
    Use tqdm to show progress bar
    """
    with ThreadPoolExecutor(max_workers=10) as executor:
        # executor.map returns an iterator of results
        list(
            tqdm(
                executor.map(process_device, devices),
                total=len(devices),
                desc="Processing devices",
                unit="device"
            )
        )

if __name__ == "__main__":
    # Setup logger
    os.makedirs(LOGS_DIR, exist_ok=True)
    logger = setup_logger()

    args = parse_args()

    # set console level based on --verbose flag
    console_level = logging.DEBUG if args.verbose else logging.INFO

    # create logger (file will still default to DEBUG so diffs are recorded)
    logger = setup_logger(console_level=console_level)
    
    main(args.inventory)

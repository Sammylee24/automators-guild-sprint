from netmiko import ConnectHandler
import sys
from device_list import devices
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class NetworkDevice():
    def __init__(self, ip, user, password, device_type, port, dry_run=False):
        self.ip = ip
        self.user = user
        self.password = password
        self.device_type = device_type
        self.port = port
        self.dry_run = dry_run
        self.ssh = None

    def connect(self):
        if self.dry_run:
            logging.info(f"[DRY RUN] Would connect to {self.ip}")
            return
        try:
            device_params = {
                'host': self.ip,
                'username': self.user,
                'password': self.password,
                'port': self.port,
                'device_type': self.device_type
            }
            self.ssh = ConnectHandler(**device_params)
            logging.info(f"Connected to {self.ip}")
        except Exception as e:
            logging.error(f"Error connecting to {self.ip}")
            sys.exit(1)

    def enable(self, dev_type):
        if self.dry_run:
            logging.info(f"[DRY RUN] Would enable {self.ip}")
        try:
            if self.device_type == dev_type:
                self.ssh.enable()
                logging.info(f"Enabled {self.ip} successfully.")
        except Exception as e:
            logging.error(f"Error enabling {self.ip}")
            sys.exit(1)

    def execute_command(self, commands):
        if isinstance(commands, list):
            self.commands = commands
        else:
            try:
                with open(commands) as comm_f:
                    self.commands = [line.strip() for line in comm_f if line.strip()]
            except FileNotFoundError:
                logging.error(f"Command file '{commands}' not found.")
                return

        for cmd in self.commands:
            if self.dry_run:
                logging.info(f"[DRY RUN] Would run command on {self.ip}: {cmd}")
            else:
                output = self.ssh.send_command(cmd)
                logging.info(f"Output from {self.ip} for '{cmd}':\n{output}\n")


    def execute_config(self, configs):
        if isinstance(configs, list):
            self.configs = configs
        else:
            try:
                with open(configs) as conf_f:
                    self.configs = [line.strip() for line in conf_f if line.strip()]
            except FileNotFoundError:
                logging.error(f"Config file '{configs}' not found.")
                return

        for cfg in self.configs:
            if self.dry_run:
                logging.info(f"[DRY RUN] Would send configuration to {self.ip} for {cfg}")
            else:
                output = self.ssh.send_config_set(cfg)
                logging.info(f"Output from {self.ip} for '{cfg}':\n{output}\n")

    def disconnect(self):
        if self.dry_run:
            logging.info(f"[DRY RUN] Would disconnect from {self.ip}")
            return
        try:
            self.ssh.disconnect()
            logging.info(f"Successfully disconnected from {self.ip}")
        except Exception as e:
            logging.error(f"Failure disconnecting from {self.ip}")
            sys.exit(1)

def read_lines_from_file(path):
    """
    Read non-empty, stripped lines from a file. Returns [] if file is None/empty.
    """
    if not path:
        return []
    try:
        with open(path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logging.error(f"File not found: {path}")
        return []

def process_device(dev, args, show_cmds, cfg_cmds):
    """
    Worker function run in a thread for each device.
    Returns a status string for progress reporting.
    """
    device = NetworkDevice(
        ip=dev["host"],
        user=dev["username"],
        password=dev["password"],
        device_type=dev["device_type"],
        port=dev["port"],
        dry_run=args.dry_run,
    )

    try:
        device.connect()
        # Normalize vendor default (Netmiko uses 'cisco_ios')
        vendor = args.vendor or "cisco_ios"
        device.enable(dev_type=vendor)
        device.execute_config(cfg_cmds)
        device.execute_command(show_cmds)
        device.disconnect()
        return f"{dev['host']}: OK"
    except Exception as e:
        # Ensure we attempt to disconnect if something failed mid-stream
        try:
            device.disconnect()
        except Exception:
            pass
        return f"{dev['host']}: ERROR ({e})"

def main():
    parser = argparse.ArgumentParser(description="Network Automation (multithreaded + progress)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate execution without connecting to devices")
    parser.add_argument("--commands", default="commands.txt", help="File containing show/exec commands")
    parser.add_argument("--configs", default="configs.txt", help="File containing configuration commands")
    parser.add_argument("--log", default="log.txt", help="Log file path")
    parser.add_argument("--vendor", default="cisco_ios", help="Device vendor/platform (e.g., cisco_ios)")
    parser.add_argument("--workers", type=int, default=5, help="Max number of devices to process in parallel")
    args = parser.parse_args()

    logging.basicConfig(
        filename=args.log,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Read command files once and share across threads
    show_cmds = read_lines_from_file(args.commands)
    cfg_cmds = read_lines_from_file(args.configs)

    total = len(devices)
    if total == 0:
        print("No devices found in device_list.devices")
        return

    # Progress bar setup (tqdm if available; else simple prints)
    if tqdm:
        pbar = tqdm(total=total, desc="Processing devices", unit="device")
    else:
        pbar = None
        print(f"Processing {total} device(s)...")

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_map = {executor.submit(process_device, dev, args, show_cmds, cfg_cmds): dev for dev in devices}
        for future in as_completed(future_map):
            res = future.result()
            results.append(res)
            # Update progress
            if pbar:
                pbar.update(1)
            else:
                print(res)

    if pbar:
        pbar.close()

    # Print a concise summary to stdout (logs already contain full details)
    print("\nRun summary:")
    for r in results:
        print(" -", r)


if __name__ == "__main__":
    main()

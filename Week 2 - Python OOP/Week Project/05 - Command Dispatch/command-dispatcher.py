from netmiko import ConnectHandler
import sys
from device_list import devices
import logging
import argparse

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

    def execute_command(self, command_file):
        try:
            with open(command_file) as comm_f:
                self.commands = [line.strip() for line in comm_f if line.strip()]
        except FileNotFoundError:
            logging.error(f"Command file '{command_file}' not found.")
            return

        for cmd in self.commands:
            if self.dry_run:
                logging.info(f"[DRY RUN] Would run command on {self.ip}: {cmd}")
            else:
                output = self.ssh.send_command(cmd)
                logging.info(f"Output from {self.ip} for '{cmd}':\n{output}\n")

    def execute_config(self, config_file):
        try:
            with open(config_file) as conf_f:
                self.configs = [line.strip() for line in conf_f if line.strip()]
        except FileNotFoundError:
                logging.error(f"Config file '{config_file}' not found.")
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

def main():
    parser = argparse.ArgumentParser(description="Network Automation Script")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without connecting to devices"
    )
    parser.add_argument(
        "--commands",
        default="commands.txt",
        help="File containing show commands"
    )
    parser.add_argument(
        "--configs",
        default="configs.txt",
        help="File containing configuration commands"
    )
    parser.add_argument(
        "--log",
        default="log.txt",
        help="Log file path"
    )
    parser.add_argument(
        "--vendor",
        default='cisco-ios',
        help="What device vendor?"
    )

    args = parser.parse_args()

    logging.basicConfig(
            filename=args.log,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
        )

    for dev in devices:
        device = NetworkDevice(
            ip=dev['host'],
            user=dev['username'],
            password=dev['password'],
            device_type=dev['device_type'],
            port=dev['port'],
            dry_run=args.dry_run
        )

        device.connect()
        device.enable(dev_type=args.vendor)
        device.execute_config(config_file=args.configs)
        device.execute_command(command_file=args.commands)
        device.disconnect()

if __name__ == "__main__":
    main()

from netmiko import ConnectHandler
import sys
from device_list import devices
import logging

class NetworkDevice():
    def __init__(self, ip, user, password, device_type, port):
        self.ip = ip
        self.user = user
        self.password = password
        self.device_type = device_type
        self.port = port

    def connect(self):
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

    def enable(self):
        try:
            if self.device_type == 'cisco_ios':
                self.ssh.enable()
                logging.info(f"Enabled {self.ip} successfully.")
        except Exception as e:
            logging.error(f"Error enabling {self.ip}")
            sys.exit(1)

    def execute_command(self, command_file):
        try:
            self.commands = self.ssh.send_config_from_file(command_file)
            logging.info(f"Executed commands on {self.ip} successfully")
        except Exception as e:
            logging.error(f"Failure delivering commands to {self.ip}")
            sys.exit(1)

    def execute_config(self, config_file):
        try:
            self.configs = self.ssh.send_config_from_file(config_file)
            logging.info(f"Executed configurations on {self.ip} successfully")
        except Exception as e:
            logging.error(f"Failure delivering configurations to {self.ip}")
            sys.exit(1)

    def log_actions(self, log_file):
        try:
            logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
        )
        except Exception as e:
            print(e)

    def disconnect(self):
        try:
            self.ssh.disconnect()
            logging.info(f"Successfully disconnected from {self.ip}")
        except Exception as e:
            logging.error(f"Failure disconnecting from {self.ip}")
            sys.exit(1)

def main():
    command_file = 'commands.txt'
    config_file = 'configs.txt'
    logfile = 'log.txt'

    logging.basicConfig(
            filename=logfile,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
        )

    for dev in devices:
        device = NetworkDevice(
            ip=dev['host'],
            user=dev['username'],
            password=dev['password'],
            device_type=dev['device_type'],
            port=dev['port']
        )

        device.connect()
        device.enable()
        device.execute_command(command_file=command_file)
        device.execute_config(config_file=config_file)
        device.disconnect()

if __name__ == "__main__":
    main()

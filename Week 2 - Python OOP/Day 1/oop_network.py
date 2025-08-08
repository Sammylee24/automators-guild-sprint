class NetworkDevice():
    def __init__(self, hostname, ip, vendor, model, os):
        self.hostname = hostname
        self.ip = ip
        self.vendor = vendor
        self.model = model
        self.os = os

    def display_info(self):
        print(f"Hostname is {self.hostname}")
        print(f"IP Address is {self.ip}")
        print(f"Vendor is {self.vendor}")
        print(f"Model is {self.model}")
        print(f"OS is {self.os}")
        print("-" * 30)

class Router(NetworkDevice):
    def __init__(self, hostname, ip, vendor, model, os):
        super().__init__(hostname, ip, vendor, model, os)
        self.routing_protocols = []

    def add_protocol(self, protocol):
        if protocol not in self.routing_protocols:
            self.routing_protocols.append(protocol)

    def display_info(self):
        super().display_info()
        print(f"Routing protocol {self.routing_protocols}")
        print("-" * 30)

class Switch(NetworkDevice):
    def __init__(self, hostname, ip, vendor, model, os, number_of_ports):
        super().__init__(hostname, ip, vendor, model, os)
        self.number_of_ports = number_of_ports

    def show_ports(self):
        print(f"Number of ports is {self.number_of_ports}")

    def display_info(self):
        super().display_info()
        print(f"{self.hostname} has {self.number_of_ports} ports")
        print("-" * 30)

def main():
    # Creare Routers
    r1 = Router("R1", "192.168.1.1", "Huawei", "NetEngine 8000", "VRP")
    r1.add_protocol("OSPF")
    r1.add_protocol("BGP")

    r2 = Router("R2", "192.168.1.2", "Cisco", "ISR", "IOS")
    r2.add_protocol("IS-IS")

    # Create Switches
    s1 = Switch("S1", "192.168.2.1", "Huawei", "CE6881", "VRP", "48")
    s2 = Switch("S2", "192.168.2.2", "Cisco", "Catalyst 9300", "IOS-XE 17.3", 48)

    # Display all device info
    for device in [r1, r2, s1, s2]:
        device.display_info()

    # Show switch ports
    s1.show_ports
    s2.show_ports

if __name__ == "__main__":
    main()

import random

class NetworkDevice():
    def __init__(self, hostname, ip_address, vendor, os_version):
        self.hostname = hostname
        self.ip_address = ip_address
        self.vendor = vendor
        self.os_version = os_version

    def ping(self):
        info = random.choice(["Online", "Offline"])
        return f"{self.ip_address} is {info}"
    
class Router(NetworkDevice):
    def __init__(self, hostname, ip_address, vendor, os_version):
        super().__init__(hostname, ip_address, vendor, os_version)
        self.routing_table = []

    def add_route(self, destination, next_hop):
        if destination and next_hop not in self.routing_table:
            self.routing_table.append((destination, next_hop))

class Switch(NetworkDevice):
    def __init__(self, hostname, ip_address, vendor, os_version):
        super().__init__(hostname, ip_address, vendor, os_version)
        self.vlans = []

    def add_vlan(self, vlan_id):
        if vlan_id not in self.vlans:
            self.vlans.append(vlan_id)

class Firewall(NetworkDevice):
    def __init__(self, hostname, ip_address, vendor, os_version):
        super().__init__(hostname, ip_address, vendor, os_version)
        self.rules = []

    def add_rule(self, rule):
        #if rule not in self.add_rule:
        self.rules.append(rule)      

class NetworkInventory:
    def __init__(self):
        self.devices = []

    def add_device(self, device):
        if device not in self.devices:
            self.devices.append(device)

    def display_info(self):
        print("\nHostname"," "*10,"IP Address"," "*10,"Vendor"," "*10,"OS Version"," "*10)
        print("-"*80)
        for device in self.devices:
            print(f"{device.hostname:<20}{device.ip_address:<20}{device.vendor:<20}{device.os_version:<20}")
        print("-"*80,"\n")

    def search_device(self, query):
        for device in self.devices:
            if query == device.ip_address or query == device.hostname:
                return device
        return None

def main():
    r1 = Router("R1", "192.168.1.1", "Huawei", "VRP")
    r1.add_route("20.0.0.0/24", "192.168.1.254")
    r1.add_route("0.0.0.0/0", "10.10.2.254")
    print(r1.ping())

    r2 = Router("R2", "192.168.1.2", "Cisco", "IOS")
    r2.add_route("20.0.0.0/24", "192.168.1.254")
    r2.add_route("0.0.0.0/0", "10.10.2.254")
    print(r2.ping())

    sw1 = Switch("SW1", "192.168.2.1", "Huawei", "VRP")
    sw1.add_vlan("200 to 220")
    sw1.add_vlan("4000")
    print(sw1.ping())

    sw2 = Switch("SW2", "192.168.2.2", "Cisco", "IOS")
    sw2.add_vlan("200 to 220")
    print(sw2.ping())

    fw1 = Firewall("FW1", "192.168.3.1", "Huawei", "VRP")
    fw1.add_rule("Allow 192.168.1.0/24 reach 0.0.0.0/0")
    print(fw1.ping())

    fw2 = Firewall("FW2", "192.168.3.2", "Huawei", "VRP")
    fw2.add_rule("Allow 192.168.1.0/24 reach 0.0.0.0/0")
    print(fw2.ping())

    inventory = NetworkInventory()
    inventory.add_device(r1)
    inventory.add_device(r2)
    inventory.add_device(sw1)
    inventory.add_device(sw2)
    inventory.add_device(fw1)
    inventory.add_device(fw2)

    inventory.display_info()
    to_search = "R1"
    found = inventory.search_device(to_search)
    if found:
        print("Found: ", found.hostname, found.ip_address)
    else:
        print("Device not found")

if __name__ == "__main__":
    main()

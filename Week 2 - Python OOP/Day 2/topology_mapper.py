class NetworkDevice():
    def __init__(self, hostname, ip_address):
        self.hostname = hostname
        self.ip_address = ip_address
    
class Router(NetworkDevice):
    def __init__(self, hostname, ip_address):
        super().__init__(hostname, ip_address)

class Switch(NetworkDevice):
    def __init__(self, hostname, ip_address):
        super().__init__(hostname, ip_address)

class Firewall(NetworkDevice):
    def __init__(self, hostname, ip_address):
        super().__init__(hostname, ip_address)

class NetworkTopology:
    def __init__(self):
        self.devices = []
        self.links = []

    def add_device(self, device):
        if device not in self.devices:
            self.devices.append(device)

    def add_link(self, device_a, interface_a, device_b, interface_b):
        if device_a not in self.links:
            self.links.append({
                "device_a": device_a.hostname,
                "interface_a": interface_a,
                "device_b": device_b.hostname,
                "interface_b": interface_b
            })

    def display_topo(self):
        print("\nDevice A"," "*10,"Interface A"," "*10,"Device B"," "*10,"Interface B"," "*10)
        print("-"*80)
        for link in self.links:
            print(f"{link['device_a']:<20}{link['interface_a']:<20}{link['device_b']:<20}{link['interface_b']:<20}")
        print("-"*80,"\n")

    def search():
        pass

    def export_topo():
        pass

def main():
    r1 = Router("R1", "192.168.1.1")
    r2 = Router("R2", "192.168.1.2")#
    sw1 = Switch("SW1", "192.168.2.1")
    sw2 = Switch("SW2", "192.168.2.2")
    fw1 = Firewall("FW1", "192.168.3.1")
    fw2 = Firewall("FW2", "192.168.3.2")

    topology = NetworkTopology()
    topology.add_device(r1)
    topology.add_device(r2)
    topology.add_device(sw1)
    topology.add_device(sw2)
    topology.add_device(fw1)
    topology.add_device(fw2)

    topology.add_link(r1, "e0/0", sw1, "e0/0")
    topology.add_link(r1, "e0/1", sw2, "e0/0")
    topology.add_link(r2, "e0/0", sw1, "e0/1")
    topology.add_link(r2, "e0/0", sw2, "e0/1")
    topology.add_link(fw1, "e0/0", sw1, "e0/2")
    topology.add_link(fw1, "e0/1", sw2, "e0/2")
    topology.add_link(fw2, "e0/0", sw1, "e0/3")
    topology.add_link(fw2, "e0/1", sw2, "e0/3")

    topology.display_topo()

if __name__ == "__main__":
    main()

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

class NetworkTopology():
    def __init__(self):
        self.devices = []
        self.links = []

    def add_device(self, hostname):
        if hostname not in self.devices:
            self.devices.append(hostname)

    def add_links(self, hostname_a, interface_a, hostname_b, interface_b):
        if hostname_a not in self.links:
            self.links.append({
                "hostname_a": hostname_a.hostname,
                "interface_a": interface_a,
                "hostname_b": hostname_b.hostname,
                "interface_b": interface_b
            })

    def display_topo(self):
        print("\nDevice A"," "*10,"Interface A"," "*10,"Device B"," "*10,"Interface B"," "*10)
        print("-"*80)
        for link in self.links:
            print(f"{link['hostname_a']:<20}{link['interface_a']:<20}{link['hostname_b']:<20}{link['interface_b']:<20}")
        print("-"*80,"\n")

    def search(self, device_name):
        connected = []
        for link in self.links:
            if link['hostname_a'] == device_name:
                connected.append(link['hostname_b'])
            elif link['hostname_b'] == device_name:
                connected.append(link['hostname_a'])
        return connected

    def export(self, filename):
        with open(filename, "w") as export:
            export.write("Network Topology\n")
            export.write("=======================\n")
            for link in self.links:
                export.write(f"{link['hostname_a']} <--> {link['hostname_b']}\n")

def main():
    r1 = Router("R1", "192.168.1.1")
    r2 = Router("R2", "192.168.1.2")
    sw1 = Switch("SW1", "192.168.2.1")
    sw2 = Switch("SW2", "192.168.2.2")

    topology = NetworkTopology()
    
    topology.add_device(r1)
    topology.add_device(r2)
    topology.add_device(sw1)
    topology.add_device(sw2)

    topology.add_links(r1, "e0/0", r2, "e0/0")
    topology.add_links(sw1, "e0/0", sw2, "e0/0")
    topology.add_links(r1, "e0/1", sw1, "e0/1")
    topology.add_links(r1, "e0/2", sw2, "e0/1")
    topology.add_links(r2, "e0/1", sw1, "e0/2")
    topology.add_links(r2, "e0/2", sw2, "e0/2")

    to_search = "SW2"
    topology.display_topo()
    topology.export("export.txt")
    print("Devices connected to", to_search, "are:", topology.search(to_search))

if __name__ == "__main__":
    main()

# This code receives device name and interface in a list
# Group them in dictionary mapping - devices and interface

list = [
    "Access-01_e0/0", "Access-02_e0/0", "Access-03_e0/0", "Access-04_e0/0", 
    "Access-05_e0/1", "Access-06_e0/1", "Access-07_e0/1", "Access-08_e0/1", 
    "Access-09_e0/2", "Access-10_e0/2", "Access-11_e0/2", "Access-12_e0/2"
]

devices = []
interfaces = []

for i in list:
    try:
        device = i.split('_')[0]
        devices.append(device)
        interface = i.split('_')[-1]
        interfaces.append(interface)
    except Exception as e:
        print("An error occured ---", e)
    
final_dict = {'devices':devices, 'interfaces':interfaces}
print(final_dict)

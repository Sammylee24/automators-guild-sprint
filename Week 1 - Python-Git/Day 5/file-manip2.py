ip_list = []
count = 0

with open('ips.txt', 'r') as file:
    ips = file.readlines()
    for ip in ips:
        ip_list.append(ip)
        count += 1
    print(ip_list)
    print("Total of", count, "IPs.")

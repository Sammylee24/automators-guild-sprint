from netmiko import ConnectHandler

router = {
    'device_type': 'cisco_ios',
    'host': '192.168.220.50',
    'username': 'Samuel',
    'password': 'Samuel@1234',
    'port': 22
}

ssh = ConnectHandler(**router)
ssh.enable()
result = ssh.send_command('show ip int b')
print(result)
dsd

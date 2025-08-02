# Import relevant modules
from device_list import devices
from network_utils import connect_device, enable_device, execute_command, device_disconnect

# Loop through all devices
for device in devices:
    try:
        # Connect to device
        conn = connect_device(device)

        if conn:
            # Enter enable mode
            enable_device(conn, device)
            # Perform command execution
            output = execute_command(conn, 'show ip int b')
            print(output)
            # Disconnect from device
            device_disconnect(conn)
        else:
            print("[-] Skipping",device['host'])
            
    except Exception as exception:
        print(exception)

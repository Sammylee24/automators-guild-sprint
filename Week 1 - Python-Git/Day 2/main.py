# Import relevant modules
from info import devices, commands
from network_utils import connect_device, enable_device, execute_command, device_disconnect, config_device, file_config

# Loop through all devices
for device in devices:
    try:
        # Connect to device
        conn = connect_device(device)

        if conn:
            # Enter enable mode
            enable_device(conn, device)

            # Perform command execution
            output1 = execute_command(conn, 'show ip int b')
            output2 = config_device(conn, commands)
            output3 = file_config(conn, 'file-config.txt')
            print(output1, "\n")
            print(output2, "\n")
            print(output3, "\n")

            # Disconnect from device
            device_disconnect(conn)
        else:
            print("[-] Skipping",device['host'])
            
    except Exception as exception:
        print(exception)

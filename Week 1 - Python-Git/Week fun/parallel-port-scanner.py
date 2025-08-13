import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

host = '192.168.2.1'

def local_socket(port):
    try:
        # Create socket object
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.settimeout(0.5)
        result = server_socket.connect_ex((host, port))
        if result == 0:
            return f"✅ Port {port} is OPEN on {host}"
        else:
            return None
    except Exception as e:
        print(e)

def main():
    ports = range(1,100)

    with ThreadPoolExecutor(max_workers=50) as executor:
        try:
            futures = {executor.submit(local_socket, port): port for port in ports}
            
            for future in tqdm(as_completed(futures), total=len(futures), desc="Scanning Ports"):
                result = future.result()
                if result:
                    print(result)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    main()

from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime
import threading

run_time = datetime.now()

def fake_connect(device_id):
    start_time = datetime.now()
    print(f"Connecting to device {device_id} at {start_time}")
    time.sleep(2)
    end_time = datetime.now()
    print(f"Finished connecting to {device_id} at {end_time}")
    print(f"Finished processing {device_id} in {end_time - start_time} using {threading.current_thread().name}")
    # print(threading.current_thread().name)

devices = []
for i in range(1,6):
    device_name = f"Device-{i}"
    devices.append(device_name)

with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(fake_connect, devices)

print(f"Code run time: {datetime.now() - run_time}")

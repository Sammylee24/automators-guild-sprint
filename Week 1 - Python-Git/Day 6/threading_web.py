from concurrent.futures import ThreadPoolExecutor
import threading
import time
import random
from datetime import datetime

start_time = datetime.now()

def fake_web_scrap(site):
    print(f"[{threading.current_thread().name}] Started scrape site: {site}")
    wait_time = random.randint(a=1, b=3)
    time.sleep(wait_time)

websites = ["samuel.com", "testtest.lol", "lol.lol.com", "today.lol", "fake.fake"]

with ThreadPoolExecutor(max_workers=3) as executor:
    list(executor.map(fake_web_scrap, websites))

print(f"Scraping completed at {datetime.now() - start_time}")

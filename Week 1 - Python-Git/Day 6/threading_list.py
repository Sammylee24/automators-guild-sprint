from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

time_now = datetime.now()

def square(n):
    return n * n

numbers = [1, 2, 3, 4, 5]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(square, numbers))

print("Squares:", results)

print(datetime.now() - time_now)

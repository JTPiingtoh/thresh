
import requests
import asyncio
import time

import random

from thresh.ratelimiter import LeakyBucket


URL = "http://127.0.0.1:5000"
request_num = 200000

# requests:second, same as test_server rate_limit
bucket = LeakyBucket(rate=20/1, tolerance=0.01)

start = time.time()
end = 0

for i in range(request_num):

    time.sleep(0.001)
   

    if not bucket.accept_request():
        # print("rejected")
        continue

    response = requests.get(URL)
    if response.status_code == 429:
        print("Got 429!")
        end = time.time()
        print(end - start)
        break

    print(f"requests remaining: {response.headers["X-My-Remaining"]}")











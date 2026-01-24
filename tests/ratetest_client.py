
import requests
import asyncio
import time

import random

from thresh.ratelimiter import API_Key_Bucket_state

# TODO: implement async client




URL = "http://127.0.0.1:5000"
request_num = 200000

with API_Key_Bucket_state() as bucket:

    for i in range(request_num):

        time.sleep(0.001)

        if not bucket.accept_request():
            # print("rejected")
            continue

        response = requests.get(URL)
        if response.status_code == 429:
            print("Got 429!")
            end = time.time()
            break

        print(f"requests remaining: {response.headers["X-My-Remaining"]}")


response = requests.get(URL)












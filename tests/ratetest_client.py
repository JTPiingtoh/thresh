
import requests
import asyncio
import time

import random

from thresh.clients import RiotAPIClient

# TODO: implement async client


URL = "http://127.0.0.1:5000"
request_num = 200000

with RiotAPIClient() as client:

    for i in range(request_num):

        time.sleep(0.001)

        if not client.accept_request():
            # print("rejected")
            continue

        response = requests.get(URL)
        if response.status_code == 429:
            print("Got 429!")
            end = time.time()
            break

        print(f"requests remaining: {response.headers["X-My-Remaining"]}")


response = requests.get(URL)












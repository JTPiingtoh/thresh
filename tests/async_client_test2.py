import asyncio
import time

from thresh.clients import RiotAPIClient
from thresh.concurrency import concurrently_request, eagerly_concurrently_request

async def main():
    async with RiotAPIClient.connect() as client:
        
        parameters = {"region": "euw1", "tier": "DIAMOND", "division": "I"}
        inputs = [parameters for _ in range(200)]

        
    
        concurrent_start = time.time()
        results = concurrently_request(client.get_from_test_url, inputs, max_concurrent=100) 

        async for result in results:
            print(result)
        concurrent_end = time.time()


        eager_concurrent_start = time.time()
        results = eagerly_concurrently_request(client.get_from_test_url, inputs, max_concurrent=100) 

        async for result in results:
            print(result)
        eager_concurrent_end = time.time()


        sequencial_start = time.time()
        for _ in range(600):
            result = await client.get_from_test_url(region="euw1", tier="DIAMOND", division="I")
        sequencial_end = time.time()


        print(f"concurrent duration: {concurrent_end - concurrent_start}")
        print(f"eager_concurrent duration: {eager_concurrent_end - eager_concurrent_start}")
        print(f"sequencial duration: {sequencial_end - sequencial_start}")

        


asyncio.run(main(), debug=True)
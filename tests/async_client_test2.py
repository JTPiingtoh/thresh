import asyncio
import time

from thresh.clients import RiotAPIClient
from thresh.concurrency import eagerly_concurrently_request

async def main():
    async with RiotAPIClient.connect() as client:
        
        parameters = {"region": "euw1", "tier": "DIAMOND", "division": "I"}
        inputs = [parameters for _ in range(600)]

        # TODO: change this to a taskgroup model
        
    
        concurrent_start = time.time()
        results = eagerly_concurrently_request(client.get_from_test_url, inputs, max_concurrent=1) 

        async for result in results:
            ...
        concurrent_end = time.time()


        sequencial_start = time.time()
        for _ in range(600):
            result = await client.get_from_test_url(region="euw1", tier="DIAMOND", division="I")
        sequencial_end = time.time()


        print(f"concurrent duration: {concurrent_end - concurrent_start}")
        print(f"sequencial duration: {sequencial_end - sequencial_start}")

        


asyncio.run(main(), debug=True)
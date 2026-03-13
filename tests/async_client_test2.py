import asyncio

from thresh.clients import RiotAPIClient
from thresh.concurrency import concurrently_request

async def main():
    async with RiotAPIClient.connect() as client:
        
        parameters = {"region": "euw1", "tier": "DIAMOND", "division": "I"}
        inputs = [parameters for _ in range(20)]

        # TODO: change this to a taskgroup model
        
        results = concurrently_request(client.get_from_test_url, inputs, max_concurrent=1) 
        async for result in results:
            ...

        # for _ in range(10):
        #     result = await client.get_from_test_url(region="euw1", tier="DIAMOND", division="I")


        


asyncio.run(main(), debug=True)
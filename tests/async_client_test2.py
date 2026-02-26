import asyncio

from thresh.clients import RiotAPIClient


async def main():
    async with RiotAPIClient.connect() as client:
        
        option = {"region" : "euw1", "tier": "DIAMOND"}
        parameter_iterable = [option for _ in range(100)]

        results = await client.get_from_test_url(parameter_iterable=parameter_iterable)

asyncio.run(main(), debug=True)
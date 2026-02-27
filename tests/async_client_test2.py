import asyncio

from thresh.clients import RiotAPIClient


async def main():
    async with RiotAPIClient.connect() as client:
        
        option = {"tier": "DIAMOND"}
        parameter_iterable = [option for _ in range(2)]

        results = await client.get_from_test_url(region="euw1", parameter_iterable=parameter_iterable)
        results = await client.get_from_test_url(region="euw1", tier="DIAMOND")

asyncio.run(main(), debug=True)
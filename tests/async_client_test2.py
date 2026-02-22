import asyncio

from thresh.clients import RiotAPIClient


async def main():
    async with RiotAPIClient.connect() as client:
        
        option = {"region" : "foo", "tier": "foo"}
        options = [option for _ in range(1000)]

        results = await client.get_from_test_url(options=options)

asyncio.run(main(), debug=True)
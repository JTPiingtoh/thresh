import asyncio

from thresh.clients import RiotAPIClient


async def main():
    async with RiotAPIClient.connect() as client:
        

        # TODO: change this to a taskgroup model
        results = await client.get_from_test_url(region="euw1", tier="DIAMOND", division="I")

        


asyncio.run(main(), debug=True)
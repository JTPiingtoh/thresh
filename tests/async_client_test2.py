import asyncio

from thresh.clients import RiotAPIClient


async def main():
    async with RiotAPIClient.connect() as client:
        
        option = {"tier": "DIAMOND", "division": "I"}
        parameter_iterable = [option for _ in range(100)]

        # TODO: change this to a taskgroup model
        results = await client.get_from_test_url(region="euw1", parameter_iterable=parameter_iterable)
        # results = await client.get_from_test_url(region="euw1", tier="DIAMOND", division="I")

        i = 0
        async for result in results:
            print(result)

asyncio.run(main(), debug=True)
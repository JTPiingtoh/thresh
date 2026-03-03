import asyncio

from thresh.clients import RiotAPIClient
from thresh.task_group import RiotAPIGroupedRequest

async def main():
    async with RiotAPIClient.connect() as client:
        
        option = {"tier": "DIAMOND", "division": "I"}
        parameter_iterable = [option for _ in range(100)]

        # TODO: change this to a taskgroup model
        results = await client.get_from_test_url(region="euw1", parameter_iterable=parameter_iterable)
        # results = await client.get_from_test_url(region="euw1", tier="DIAMOND", division="I")

        
        async with RiotAPIGroupedRequest() as gr:
            for result in results:
                gr.add_request(client.get_from_test_url(...))

            results_2 = await gr.results()

            for r2 in results_2:
                ...

asyncio.run(main(), debug=True)
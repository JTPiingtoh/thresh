import asyncio

from thresh.clients import RiotAPIClient


async def main():
    async with RiotAPIClient.connect() as client:
        
        try:
            for i in range(200):
                text = await client.get_from_test_url()
                print(text.get('X-App-Rate-Limit'))
        except RuntimeError as e:
            print(e)

asyncio.run(main(), debug=True)
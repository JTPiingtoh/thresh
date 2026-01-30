import aiohttp
import asyncio

from thresh.ratelimiters import RiotAPILimiter

URL = "http://127.0.0.1:5000"

limiter = RiotAPILimiter(10/1)

async def handle_request(url, data_list: list):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:

            if resp.status == 429:
                raise RuntimeError("429")

            print(dict(resp.headers))


            data_list.append(await resp.text())
                        

async def main():
        
        data_list = []
        urls = [URL] * 21

        async with asyncio.TaskGroup() as tg:
            for url in urls:
                
                await limiter._acceptable_request()
                task = tg.create_task(handle_request(URL, data_list))

        print(data_list)
                


asyncio.run(main())
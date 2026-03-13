import asyncio
from typing import Iterable, Coroutine, Any, AsyncIterator, Callable

import aiohttp

from thresh.clients import RiotAPIClient

# BUG: is creating a new rate_limit instance
async def concurrently_request[I,O](
    request: Callable[[I], Coroutine[Any, Any, O]], 
    inputs: AsyncIterator[I],
    max_concurrent: int = 1) -> AsyncIterator[O]:
    
    semaphore = asyncio.Semaphore(max_concurrent)

    async def do_request(input):
        async with semaphore:
            return await request(**input)

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(do_request(input)) for input in inputs]

        # TODO: check order!
    
    for task in tasks:
        yield task.result()
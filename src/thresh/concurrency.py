import asyncio
from typing import Iterable, Coroutine, Any, AsyncIterator, Callable

import aiohttp

from thresh.clients import RiotAPIClient

async def eagerly_concurrently_request[I,O](
    request: Callable[[I], Coroutine[Any, Any, O]], 
    inputs: AsyncIterator[I] | Iterable[I],
    max_concurrent: int = 1) -> AsyncIterator[O]:
    '''
    Eagerly request from the supplied API endpoint. Returns a ...
    object.
    '''

    semaphore = asyncio.Semaphore(max_concurrent)

    async def do_request(input):
        async with semaphore:
            return await request(**input)

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(do_request(input)) for input in inputs]

    
    for task in tasks:
        yield task.result()
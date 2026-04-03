import asyncio
from typing import Iterable, Coroutine, Any, AsyncIterator, Callable


from thresh.clients import RiotAPIClient

type I = dict[str, int | str]

async def concurrently_request[O](
    request: Callable[..., Coroutine[Any, Any, O]], 
    inputs: Iterable[dict[str, str | int]],
    max_concurrent: int = 1) -> AsyncIterator[O]:
    '''
    Concurrently request from the supplied API endpoint. Returns a ...
    object.
    '''

    semaphore = asyncio.Semaphore(max_concurrent)

    async def do_request(input: I):
        async with semaphore:
            return await request(**input)

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(do_request(input)) for input in inputs]

    
    for task in tasks:
        yield task.result()


async def eagerly_concurrently_request[O](
    request: Callable[..., Coroutine[Any, Any, O]], 
    inputs: Iterable[dict[str, str | int]],
    max_concurrent: int = 1) -> AsyncIterator[O]:
    '''
    Concurrently request from supplied endpoint. Results are yeilded eagerly.
    '''
    
    semaphore = asyncio.Semaphore(max_concurrent)

    async def do_request(input: I):
        async with semaphore:
            return await request(**input)

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(do_request(input)) for input in inputs]

        async for task in asyncio.as_completed(tasks):
            yield task.result()
    
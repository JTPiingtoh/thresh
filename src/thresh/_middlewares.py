import asyncio
from typing import Callable

import aiohttp
from aiohttp import ClientRequest, ClientHandlerType, ClientResponse
from thresh.request_object import RequestObject
from thresh.ratelimiters import BaseRateLimiter



async def _ratelimit_middleware(request_object: RequestObject, next: callable) -> ClientResponse:
    
    rate_limiter: BaseRateLimiter = request_object._rate_limiter
    parameters: dict = request_object._parameters

    while True:
        print("Wait")
        wait_for: float = await rate_limiter.compute_wait_for(parameters)
        if wait_for == rate_limiter.NOT_WAIT_FLAG or wait_for == rate_limiter.SYNC_FLAG:
            break
        await asyncio.sleep(wait_for)

    response: ClientResponse = await next(request_object)
    await rate_limiter.sync(wait_for, parameters)
    return response


async def _retry_middleware(request_object: RequestObject, next: Callable) -> ClientResponse:
    
    for _ in range(3):
        response: aiohttp.ClientResponse = await next(request_object)

        if response.ok:
            return response
        
    return response


async def json_response_middleware(request_object: RequestObject, next: Callable):
    ...

    



    

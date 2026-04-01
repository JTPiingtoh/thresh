import asyncio
from typing import Callable

import aiohttp
from aiohttp import ClientRequest, ClientHandlerType, ClientResponse
from thresh.request_object import RequestObject
from thresh.ratelimiters import BaseRateLimiter, WaitFlags


# TODO: This needs to be changed to a class, and the request object should not have a reference of the rl
async def _ratelimit_middleware(request_object: RequestObject, next: Callable) -> ClientResponse:
    
    rate_limiter: BaseRateLimiter = request_object._rate_limiter
    parameters: dict = request_object._parameters

    while True:
        wait_for: float = await rate_limiter.compute_wait_for(parameters)
        if WaitFlags.conforming(wait_for=wait_for):
            break
        await asyncio.sleep(wait_for)

    response: ClientResponse = await next(request_object)
    if WaitFlags.sync_required(wait_for):
        try:
            await rate_limiter.sync(parameters, response.headers)
        except AttributeError as e:
            print("http response lacks headers")
            raise            
    return response


async def _retry_middleware(request_object: RequestObject, next: Callable) -> ClientResponse:
    
    response: ClientResponse = await next(request_object)

    for _ in range(2):
        if response.ok:
            break
        response = await next(request_object)


    return response


async def json_response_middleware(request_object: RequestObject, next: Callable):
    ...

    



    

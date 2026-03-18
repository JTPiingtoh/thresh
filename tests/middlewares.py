import asyncio
from typing import Callable

import aiohttp

from thresh.ratelimiters import BaseRateLimiter
from thresh.request_object import RequestObject

def rate_limiter_middleware(rate_limiter: BaseRateLimiter):
    async def middleware(input: RequestObject, next: Callable):
        region = input.parameters["region"]

        while True:
            wait_for = await rate_limiter.compute_wait_for(region)
            if wait_for <= 0:
                break
            await asyncio.sleep(wait_for)

        response: aiohttp.ClientResponse = await next(input)

        if wait_for == -1:
            await rate_limiter.sync_limiter(region, response.headers)

        return response
    
    return middleware
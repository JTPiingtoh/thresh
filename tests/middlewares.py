import asyncio
from typing import Callable

import aiohttp

from thresh.ratelimiters import BaseRateLimiter
from thresh.request_object import RequestObject

class rate_limiter_middleware:

    # TODO: dependancy injector needs to be able to init this object
    # dependacny injector needs to know that this class needs a ratelimiter from the requestobject
    def __init__(self, rate_limiter: BaseRateLimiter):
        self.rate_limiter = rate_limiter


    async def __call__(self, input: RequestObject, next: Callable):
        region = input.parameters["region"]
        rate_limiter: BaseRateLimiter = self.rate_limiter

        while True:
            wait_for = await rate_limiter.compute_wait_for(region)
            if wait_for <= 0:
                break
            await asyncio.sleep(wait_for)

        response: aiohttp.ClientResponse = await next(input)

        if wait_for == -1:
            await rate_limiter.sync_limiter(region, response.headers)

        return response

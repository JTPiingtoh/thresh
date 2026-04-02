import asyncio
from typing import Callable

from aiohttp import ClientResponse
from thresh.request_object import RequestObject
from thresh.ratelimiters import BaseRateLimiter, WaitFlags



class RateLimitMiddleware:
    def __init__(self, rate_limiter: BaseRateLimiter) -> None:
        self.rate_limiter = rate_limiter

    async def __call__(self, request_object: RequestObject, next: Callable) -> ClientResponse:
        
        rate_limiter: BaseRateLimiter = self.rate_limiter

        while True:
            wait_for: float = await rate_limiter.compute_wait_for(request_object)
            if WaitFlags.breakable(wait_for=wait_for):
                break
            await asyncio.sleep(wait_for)

        response: ClientResponse = await next(request_object)
        if WaitFlags.sync_required(wait_for):
            try:
                await rate_limiter.sync(request_object, response.headers)
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

    



    

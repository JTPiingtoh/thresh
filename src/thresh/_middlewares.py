import asyncio
from typing import Callable

from aiohttp import ClientResponse
from thresh.request_object import RequestObject
from thresh.ratelimiters import BaseRateLimiter, WaitFlags, RateLimitDecision

from typing import Callable, Awaitable


Middleware = Callable[[RequestObject], Awaitable[ClientResponse]]

class RateLimitMiddleware:
    def __init__(self, rate_limiter: BaseRateLimiter) -> None:
        self.rate_limiter = rate_limiter

    async def __call__(self, request_object: RequestObject, next: Middleware) -> ClientResponse:
        
        rate_limiter: BaseRateLimiter = self.rate_limiter

        while True:
            decision: RateLimitDecision = await rate_limiter.test_compliancy(request_object)
            if decision.is_compliant:
                break
            await asyncio.sleep(decision.retry_after)
        
        response: ClientResponse = await next(request_object)

        try:
        # Log 429 and limiter state, check header to retry
            if response.status == 429:
                await rate_limiter.handle_exceeded(request_object, response.headers)


            elif decision.should_sync:
                await rate_limiter.sync(request_object, response.headers)
        except AttributeError as e:
            raise RuntimeError("http response lacks headers")
                            
        return response

# This is intended for single requests. 
class HTTPErrorMiddleware():
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    
    async def _http_error_middleware(self, request_object: RequestObject, next: Middleware) -> ClientResponse:
        
        max_retries: int = self.max_retries 
        response: ClientResponse = await next(request_object)

        status: int = response.status

        for attempt in range(max_retries):
            wait_for: float = float(((2 ** attempt) - 1) * 0.5)
            await asyncio.sleep(wait_for)

            if status <= 400 & status < 500 & status != 429:
                break


        if status == 429:
            ...

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

    



    

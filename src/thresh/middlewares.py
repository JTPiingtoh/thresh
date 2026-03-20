import asyncio
from typing import Callable
from abc import ABC, abstractmethod

from aiohttp import ClientRequest, ClientHandlerType, ClientResponse
from thresh.request_object import RequestObject
from thresh.ratelimiters import BaseRateLimiter


class RequestMiddleware():
    '''
    Some middlewares for individual requests may need to store
    that requests's parameters. These can inheret from this class to ensure that they
    take a parameter dict upon init. 
    '''
    def __init__(self, parameters: dict):
        self.parameters = parameters
    
    @abstractmethod
    async def __call__(
        self,
        req: RequestObject,
        next: Callable) -> ClientResponse:
            pass


class RequestRateLimitMiddleware(RequestMiddleware):
    '''
    Class to rate limit a single request object
    '''

    def __init__(
        self, 
        rate_limiter: BaseRateLimiter,
        parameters: dict 
    ):
        super().__init__(parameters=parameters)        
        self.rate_limiter = rate_limiter

    async def __call__(
        self,
        request: RequestObject,
        next: Callable) -> ClientResponse:

        while True:
            wait_for = await self.rate_limiter.compute_wait_for(self.parameters)
            if wait_for <= 0:
                break
            await asyncio.sleep(wait_for)
        
        resp: ClientResponse = await next(request)
        
        if self.rate_limiter.targets_to_update:
            # call if computer_wait_for() finds headers that need to be updated
            await self.rate_limiter.sync_limiter(self.parameters)

        return resp


    

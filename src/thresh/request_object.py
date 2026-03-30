import asyncio
from typing import Final, Callable
import inspect
from functools import wraps

import aiohttp

from thresh.ratelimiters import BaseRateLimiter


class RequestObject():

    def __init__(
        self,
        base_url: str,
        parameters: dict,
        session: aiohttp.ClientSession,
        rate_limiter: BaseRateLimiter,
        middlewares: list[Callable],
        endpoint_name: str
        ):       
        self._base_url: Final[str] = base_url
        self._parameters: dict = parameters        
        self._session: Final[aiohttp.ClientSession] = session
        self._rate_limiter: Final[BaseRateLimiter] = rate_limiter
        self._middlewares: list[Callable] = middlewares
        # For more detailed tracebacks when using pipelines  
        self._endpoint_name: str = endpoint_name


    @property
    def url(self) -> str:
        try:
            return self._base_url.format(**self._parameters)
        except KeyError as e:          
            raise ValueError(f"{self._endpoint_name} is missing argument for {e}") 
        
    

    # Rate limiting is baked into request sending instead of being used as a middleware to ensure that
    # rate limiting always happens as last step before request.
    @staticmethod
    async def _final_handler(request_object: RequestObject) -> aiohttp.ClientResponse: 
        '''
        Send the request this object represents    
        '''
        session: aiohttp.ClientSession = request_object._session
        async with session.get(url=request_object.url) as resp:
            return resp
        

    @property
    def reversed_middlewares(self) -> list[Callable]:
        
        middlewares = self._middlewares
        if not middlewares:
            return middlewares
        middlewares.reverse()
        return middlewares


    @staticmethod
    def wrap(middleware, handler):
        
        async def new_handler(input):
            response = await middleware(input, handler)
            return response
        return new_handler


    async def send_request(self):
        '''
        Wrap request in middlewares
        '''

        final_handler = self._final_handler
        reversed_middlewares = self.reversed_middlewares
        if reversed_middlewares:
            for middleware in reversed_middlewares:
                # Note: wrapped used to avoid late bindings
                final_handler = self.wrap(middleware, final_handler)
            

        return await final_handler(self)
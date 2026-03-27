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
    async def _final_handler(self) -> aiohttp.ClientResponse: 
        '''
        Send the request this object represents    
        '''
        session: aiohttp.ClientSession = self._session
        async with session.get(url=self.url) as resp:
            return resp
        
    
    @staticmethod
    def wrap(middleware, handler):
        
        def new_handler(re):
            response = middleware(handler)
            return response
        return new_handler


    @property
    def reversed_middlewares(self):
        middlewares = self._middlewares
        middlewares.reverse()
        return middlewares

    async def send_request(self):
        '''
        Wrap request in middlewares
        '''

        final_handler = self._final_handler
        for middleware in self.reversed_middlewares:
            
            @wraps(final_handler)
            def new_handler(request: RequestObject):
                print("new")
                response = middleware(request, final_handler)
                return response
            
            final_handler = new_handler

        return await final_handler(self)
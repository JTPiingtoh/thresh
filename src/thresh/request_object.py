import asyncio
from typing import Final, Callable
import inspect

import aiohttp

from thresh.ratelimiters import BaseRateLimiter
from thresh.middlewares import RequestMiddleware
        
# aim of this class is to use dependancy injection to create a request
class RequestObject():

    def __init__(
        self,
        url: str,
        parameters: dict,
        session: aiohttp.ClientSession,
        middlewares: dict
        ):       
        self.url: Final[str] = url
        self.parameters: Final[dict] = parameters        
        self.session: Final[aiohttp.CLientSession] = session,
        self.middlewares: dict = middlewares

    @property
    def middlewares(self) -> list:
        '''
        If any middlewares are classes, initiate them with the request object's parameters
        '''
        initiated_middlewares = []
        for middleware in self.middlewares:
            if issubclass(middleware, RequestMiddleware):
                # Raises error if middleware class in not corrently implemented
                middleware: Callable = middleware(self.parameters)
            
            initiated_middlewares.append(middleware)

        return initiated_middlewares

    # TODO: Curren
    async def _send_request(self) -> aiohttp.ClientResponse: 
        '''
        Send the request the request object represents
        '''

        session: aiohttp.ClientSession = self.session

        async with session.get(url=self.url) as resp:
            return resp
        
    
    @staticmethod
    def wrap(middleware, handler):
    
        def new_handler():
            response = middleware(handler)
            return response
        return new_handler

    async def _build_request(self):
        '''
        Wrap request in middlewares
        '''

        self._initiate_middlewares()
        final_handler = self._send_request
        middlewares = self.middlewares.reverse()
        for middleware in self.middlewares:
            final_handler = ...

        
    async def send_request(self)
        
    
    



# Similar to request factory
class MultiRequestObject():
    ...



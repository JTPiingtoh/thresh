import asyncio
from typing import Final, Callable
import inspect

import aiohttp

from thresh.ratelimiters import BaseRateLimiter
from thresh.middlewares import RequestMiddleware
from thresh.extras.dependancy_injectors import inject_from



# aim of this class is to use dependancy injection to create a request
class RequestObject():

    def __init__(
        self,
        url: str,
        parameters: dict,
        session: aiohttp.ClientSession,
        endpoint_name: str
        ):       
        self.url: Final[str] = url
        self.parameters: Final[dict] = parameters        
        self.session: Final[aiohttp.CLientSession] = session,
        self.endpoint_name: Final[str] = endpoint_name
    
    
    @property
    def url(self) -> str:
        try:
            return self.base_url.format(**self.parameters)
        except KeyError as e:          
            raise ValueError(f"{self.endopoint_name} is missing argument for {e}") 
        

    @property
    def middlewares(self) -> list:
        '''
        If any middlewares are classes, initiate them with the request object's parameters
        '''
        
        initiated_middlewares = []
        for i, middleware in enumerate(self.middlewares):
            # Raises error if middleware class in not corrently implemented
            #   Must have __call__ method
            # inject_from must work
            if not inspect.isclass(middleware):
                continue

            try:
                middleware.__call__
            except AttributeError:
                raise AttributeError(f"middleware class {middleware} must have a __call__ method.")

            self.middlewares[i] = inject_from(middleware, self)

        return initiated_middlewares

    # TODO: Curren
    async def __call__(self) -> aiohttp.ClientResponse: 
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

        

    
    



# Similar to request factory
class MultiRequestObject():
    ...



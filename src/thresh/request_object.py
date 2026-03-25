import asyncio
from typing import Final, Callable
import inspect
from functools import wraps

import aiohttp

from thresh.ratelimiters import BaseRateLimiter
from thresh.extras.dependancy_injectors import inject_from



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
        

    @property
    def middlewares(self) -> list:
        
        for middleware in self._middlewares:
            if not inspect.isclass(middleware):
                continue
            try:
                middleware.__call__
            except AttributeError:
                raise AttributeError(f"middleware class {middleware} must have a __call__ method.")

        return self._middlewares
    

    # Rate limiting is baked into request sending instead of being used as a middleware to ensure that
    # rate limiting always happens as last step before request.
    async def _final_handler(self) -> aiohttp.ClientResponse: 
        '''
        Send a rate limited request    
        '''

        session: aiohttp.ClientSession = self._session
        rate_limiter: BaseRateLimiter = self._rate_limiter
        parameters: dict = self._parameters
        
        while True:
            wait_for: float = await rate_limiter.compute_wait_for(parameters)
            if wait_for <= 0:
                break
            await asyncio.sleep(wait_for)


        async with session.get(url=self.url) as resp:
            await rate_limiter.sync(wait_for, parameters)
            return resp
        
    
    @staticmethod
    def wrap(middleware, handler):
        
        def new_handler(re):
            response = middleware(handler)
            return response
        return new_handler


    async def _build_request(self):
        '''
        Wrap request in middlewares
        '''

        self._initiate_middlewares()
        final_handler = self._final_handler
        middlewares = self.middlewares.reverse()
        for middleware in middlewares:

            def decorator(func):
                @wraps(func)
                def new_handler(request: RequestObject):
                    response = middleware(request, final_handler)
                    return response
                return new_handler
            
            final_handler = decorator

        return final_handler()

        

    
    



# Similar to request factory
class MultiRequestObject():
    ...



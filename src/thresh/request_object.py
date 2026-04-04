import asyncio
from typing import Final, Callable
import inspect
from functools import wraps

import aiohttp
# TODO: move ALL middleware handling to the client

from thresh.typing import Region

class RequestObject():

    def __init__(
        self,
        base_url: str,
        parameters: dict,
        session: aiohttp.ClientSession,
        middlewares: list[Callable],
        endpoint_name: str,
        api_key: str
        ):       
        self._base_url: Final[str] = base_url
        self._parameters: dict[str, int | str] = parameters        
        self._session: Final[aiohttp.ClientSession] = session
        self._middlewares: list[Callable] = middlewares
        # For more detailed tracebacks when using pipelines  
        self._endpoint_name: str = endpoint_name
        self.api_key: str = api_key


    @property
    def url(self) -> str:
        try:
            return self._base_url.format(**self._parameters)
        except KeyError as e:          
            raise ValueError(f"{self._endpoint_name} is missing argument for {e}") 
        
    

    @property
    def region(self) -> Region:
        region: Region | int | None = self._parameters.get("region")
        if not isinstance(region, str):
            raise TypeError("RequestObject region must be a string")
        return region


    @property
    def reversed_middlewares(self) -> list[Callable]:
        
        middlewares = self._middlewares
        if not middlewares:
            return middlewares
        middlewares.reverse()
        return middlewares


    @staticmethod
    def wrap(middleware, handler):
        async def new_handler(request_object: RequestObject) -> aiohttp.ClientResponse:
            response = await middleware(request_object, handler)
            return response
        return new_handler


    # TODO: Currently has trust me bro pattern
    @staticmethod
    async def _final_handler(request_object: RequestObject) -> aiohttp.ClientResponse: 
        '''
        Send the request this object represents    
        '''

        headers = {
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Riot-Token": request_object.api_key
        }
        session: aiohttp.ClientSession = request_object._session
        async with session.get(url=request_object.url, headers=headers) as resp:
            return resp
        

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
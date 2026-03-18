import asyncio
from typing import Final, Iterable

import aiohttp

from thresh.ratelimiters import BaseRateLimiter
        
        
# aim of this class is to use dependancy injection to create a request
class RequestObject():

    def __init__(
        self,
        url: str,
        parameters: dict,
        session: aiohttp.ClientSession, 
        ):       
        self.url: Final[str] = url
        self.parameters: Final[dict] = parameters        
        self.session: Final[aiohttp.CLientSession] = session

    async def __call__(self) -> aiohttp.ClientResponse: 
        '''
        Send the request the request object represents
        '''
        session: aiohttp.ClientSession = self.session

        async with session.get(url=self.url) as resp:
            return resp
        
    
    



# Similar to request factory
class MultiRequestObject():
    ...



import asyncio
from typing import Final, Iterable

import aiohttp

from thresh.ratelimiters import BaseRateLimiter
        
        
# aim of this class is to use dependancy injection to create a request
class RequestObject():

    def __init__(
        self,
        parameters: dict,
        base_url: str,
        session: aiohttp.ClientSession, 
        rate_limiter: BaseRateLimiter
        ):       
        self.base_url: Final[str] = base_url
        self.parameters: Final[dict] = parameters        
        self.session: Final[aiohttp.CLientSession] = session
        self.rate_limiter: BaseRateLimiter = rate_limiter

    async def _send_request(self) -> aiohttp.ClientResponse: 
        '''
        Simple method that build url and sends request
        '''
        url: str
        try:
            url = self.base_url.format(**self.parameters)
        except KeyError as e:
            raise ValueError(f"Request is missing value for {e}")   
        session: aiohttp.ClientSession = self.session

        async with session.get(url=url) as resp:
            return resp
        

    async def handle_request(self) -> aiohttp.ClientResponse:
        '''
        Method that handles the request, applying relevent middlewares
        '''
                # BUG: This breaks when used in a task group.

        region = self.parameters["region"]

        while True:
            wait_for = await self.rate_limiter.compute_wait_for(region)
            if wait_for <= 0:
                break
            await asyncio.sleep(wait_for)

        response: aiohttp.ClientResponse = await self._send_request()

        if wait_for == -1:
            await self.rate_limiter.sync_limiter(region, response.headers)

        return response
    
    



# Similar to request factory
class MultiRequestObject():
    ...



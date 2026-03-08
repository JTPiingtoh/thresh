import asyncio
from typing import Final, Iterable

import aiohttp
from aiohttp import ClientRequest, ClientHandlerType, ClientResponse

from thresh.extras.finalisablelist import FinalisableList
from thresh.ratelimiters import BaseRateLimiter
        
        
# aim of this class is to use dependancy injection to create a request
class RequestObject():

    def __init__(
        self,
        parameters: dict,
        base_url: str,
        rate_limiter: BaseRateLimiter,
        session: aiohttp.ClientSession, 
        middlewares: FinalisableList
        ):
        
        self.base_url: Final[str] = base_url
        self.parameters: Final[dict] = parameters
        self.rate_limiter = rate_limiter
        self.session: Final[aiohttp.CLientSession] = session
        self.middlewares: FinalisableList = middlewares


    def finalise_middlewares(self):
        '''
        Finalises request middlewares by adding the ratelimiter. Middlewares cannot be changed after this method has been called
        '''
        async def middleware(
            req: ClientRequest,
            handler: ClientHandlerType) -> ClientResponse:

            while True:
                wait_for = await self.rate_limiter.compute_wait_for(self.parameters)
                if wait_for <= 0:
                    break
                await asyncio.sleep(wait_for)
            
            resp: ClientResponse = await handler(req)
            
            if self.rate_limiter.targets_to_update:
                # call if computer_wait_for() finds headers that need to be updated
                await self.rate_limiter.sync_limiter(resp.headers)

            return resp
        
        # now we ensure rate_limiter is the last middleware
        self.middlewares.append(middleware)
        self.middlewares.finalise()


    async def send_request(self): 

        url: str

        try:
            url = self.base_url.format(**self.parameters)
        except KeyError as e:
            raise ValueError(f"Request is missing value for {e}")

        self.finalise_middlewares()       
        middlewares: FinalisableList = self.middlewares
        session: aiohttp.ClientSession = self.session

        async with session.get(url=url, middlewares=middlewares) as resp:
            return await resp.text()

    
    



# Similar to request factory
class MultiRequestObject():
    ...



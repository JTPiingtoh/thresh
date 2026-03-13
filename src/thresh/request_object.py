import asyncio
from typing import Final, Iterable

import aiohttp

        
        
# aim of this class is to use dependancy injection to create a request
class RequestObject():

    def __init__(
        self,
        parameters: dict,
        base_url: str,
        session: aiohttp.ClientSession, 

        ):       
        self.base_url: Final[str] = base_url
        self.parameters: Final[dict] = parameters        
        self.session: Final[aiohttp.CLientSession] = session

    async def response(self): 

        url: str
        try:
            url = self.base_url.format(**self.parameters)
        except KeyError as e:
            raise ValueError(f"Request is missing value for {e}")   
        session: aiohttp.ClientSession = self.session

        async with session.get(url=url) as resp:
            return resp
        
    

    
    



# Similar to request factory
class MultiRequestObject():
    ...



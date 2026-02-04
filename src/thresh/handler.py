import asyncio
import aiohttp

from thresh.ratelimiters import RiotAPILimiter

class RequestHandler():

    def __init__(self, url: str, rate_limiter : RiotAPILimiter, session: aiohttp.ClientSession):
        self._url = url
        self._rate_limiter = rate_limiter
        self._session = session
    
    async def handle_request(self):

        session: aiohttp.ClientSession = self._session

        # TODO: make any other state illegal
        await self._rate_limiter.acceptable_request()
        
        async with session.get(self._url) as resp:
            ...
import asyncio
import aiohttp

from thresh.ratelimiters import RiotAPILimiter


# build request middlewares
# the user can supply plugins such as databases or caches into the middlewares,
# effectively making a pipeline
# the handler will ALWAYS add a ratelimiter and eventually some form of data
# transformer

class RequestHandler():

    def __init__(self, url: str, rate_limiter : RiotAPILimiter, session: aiohttp.ClientSession):
        self._url = url
        self._session = session
    
    async def handle_request(self):

        session: aiohttp.ClientSession = self._session
        middlewares = []
        middlewares.append(RiotAPILimiter(requests=100, window_size=120))

        session.get(self._url, middlewares=[])
        # TODO: make any other state illegal
        await self._rate_limiter.acceptable_request()
        

        async with session.get(self._url) as resp:
            ...
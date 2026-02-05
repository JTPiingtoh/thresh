from aiohttp import ClientRequest, ClientHandlerType, ClientResponse

from thresh.ratelimiters import RiotAPILimiter

async def rate_limit_middleware(
        req: ClientRequest, handler: ClientHandlerType
) -> ClientResponse:

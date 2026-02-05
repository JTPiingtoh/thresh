from dataclasses import dataclass
import pickle
from aiohttp import ClientRequest, ClientHandlerType, ClientResponse
from aiohttp.web import HTTPTooManyRequests
from thresh.ratelimiters import RiotAPILimiter

@dataclass
class ClientRateLimiterKeys:
    RIOT_API_RATELIMITER_KEY = "Client_RiotAPI_RLimiter_1.pkl"

_DEFAULT_RATE = 100/120

async def rate_limit_middleware(
        req: ClientRequest, handler: ClientHandlerType
) -> ClientResponse:
    """
        Applies ratelimiter to the request
        :param req: Description
        :type req: ClientRequest
        :param handler: Description
        :type handler: ClientHandlerType
        :return: Description
        :rtype: ClientResponse
    """
    
    # rebuild the ratelimiter's state from the cache
    limiter = RiotAPILimiter()
    try:
        with open(ClientRateLimiterKeys.LEAKYBUCKET, "rb") as file:
            rate_limiter = pickle.load(file)

    except FileNotFoundError:
        rate_limiter = RiotAPILimiter(rate=_DEFAULT_RATE)
    
    # with RiotAPIRatelimiter.awaken() as limiter:
        # limiter.limit(req, handler)

    await rate_limiter.request_accepted()
    resp = await handler(req)

    # If ratelimit was exceeded, raise warning, sleep ratelimiter per header
    # TODO: add ratelimiter state and relevent response headers
    # to log
    if resp.status == 429:
        raise HTTPTooManyRequests()

    # assess the header and update ratelimiter accordingly
    x_app_rate_limit_counts = resp.headers.get("X-App-Rate-Limit-Count")
    x_app_rate_limits = resp.headers.get("X-App-Rate-Limit")

    # TODO: add method rates         
    rate_limiter.set_state(x_app_rate_limit_counts, x_app_rate_limits)

        

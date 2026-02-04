###########################
# Ratelimiting middleware #
###########################


from dataclasses import dataclass

import aiohttp
from aiohttp import ClientRequest, ClientHandlerType
from thresh.ratelimiters import RiotAPILimiter
import pickle

_DEFAULT_RATE = 100/120


@dataclass
class ClientRateLimiterKeys:
    RIOT_API_RATELIMITER_KEY = "Client_RiotAPI_RLimiter_1.pkl"

async def rate_limit_middleware(
        req: ClientRequest, handle: ClientHandlerType
):
    limiter = RiotAPILimiter()
    try:
        with open(ClientRateLimiterKeys.LEAKYBUCKET, "rb") as file:
            rate_limiter = pickle.load(file)

    except FileNotFoundError:
        rate_limiter = RiotAPILimiter(rate=_DEFAULT_RATE)
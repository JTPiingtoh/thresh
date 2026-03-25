import asyncio
from typing import Callable
from abc import ABC, abstractmethod

import aiohttp
from aiohttp import ClientRequest, ClientHandlerType, ClientResponse
from thresh.request_object import RequestObject
from thresh.ratelimiters import BaseRateLimiter



async def retry_middleware(request_object: RequestObject, next: Callable):
    
    for _ in range(3):
        response: aiohttp.ClientResponse = await next(request_object)

        if response.ok:
            return response
    return response


async def http
    



    

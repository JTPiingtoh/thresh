import asyncio
from aiohttp import ClientRequest, ClientHandlerType, ClientResponse
from thresh.request_object import RequestObject
from thresh.ratelimiters import BaseRateLimiter

def construct_rate_limit_middleware(request_object: RequestObject, rate_limiter: BaseRateLimiter):


    async def middleware(
        req: ClientRequest,
        handler: ClientHandlerType) -> ClientResponse:

        while True:
            wait_for = await rate_limiter.compute_wait_for(request_object)
            if wait_for <= 0:
                break
            await asyncio.sleep(wait_for)
        
        resp: ClientResponse = await handler(req)
        
        if rate_limiter.targets_to_update:
            # call if computer_wait_for() finds headers that need to be updated
            await rate_limiter.sync_limiter(resp.headers)

        return resp


class ResponseFactoryMiddleWare():
    '''
    Middleware responsible for collecting response text. Also creates an event
    for when all responses have been collected. 
    '''
    
    
    def __init__(self):

        self.results = []


    # Objective is to intercept the results, parse them into a suitable format, and 
    # append them to the results
    async def __call__(
    self, req: ClientRequest, handler: ClientHandlerType
    ) -> ClientResponse:
        

        resp: ClientResponse = await handler(req)
        self.results.append(await resp.text())

        return resp 
    

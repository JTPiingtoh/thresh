import asyncio
from aiohttp import ClientRequest, ClientHandlerType, ClientResponse


async def http_errer_401_middleware(
        self, req: ClientRequest, handler: ClientHandlerType
    ) -> ClientResponse:


    ...


class Response_middleware():
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
        self.results.append(await resp.text)

        return resp 
    

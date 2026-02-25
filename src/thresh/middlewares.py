from aiohttp import ClientRequest, ClientHandlerType, ClientResponse


async def http_errer_401_middleware(
        self, req: ClientRequest, handler: ClientHandlerType
    ) -> ClientResponse:


    ...


class Response_object_maker_middleware():
    def __init__(self):

        self.results = []


    # Objective is to intercept the results, parse them into a suitable format, and 
    # append them to the results
    async def __call__(
    self, req: ClientRequest, handler: ClientHandlerType
    ) -> ClientResponse:
        
        resp: ClientResponse = await handler(req)

        self.results.append(resp.text)

        return resp 
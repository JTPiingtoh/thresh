from aiohttp import ClientRequest, ClientHandlerType, ClientResponse


async def http_errer_401_middleware(
        self, req: ClientRequest, handler: ClientHandlerType
    ) -> ClientResponse:


    ...
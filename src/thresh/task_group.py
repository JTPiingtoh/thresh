import asyncio
from asyncio import TaskGroup

from thresh.clients import RiotAPIClient

async def foo():
    async with TaskGroup() as tg:
        tg.create_task(...)

    

class RiotAPIGroupedRequest():
    def __init__(self, riot_api_client: RiotAPIClient):
        self.client = RiotAPIClient


    def

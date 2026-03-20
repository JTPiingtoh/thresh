import asyncio

from aiohttp import ClientSession

from typing import Final, Iterable, Callable, Generator, Iterator
from thresh.ratelimiters import BaseRateLimiter

class RiotAPIRequestFactory():

    def __init__(self, region: str, parameter_iterable: Iterator[dict], url_factory: Callable[[dict], str]):
        self.region: Final[str] = region
        self.parameter_iterable = parameter_iterable
        self.url_factory: Final = url_factory


    @classmethod
    def start_factory(cls, base_url: str, **kwargs) -> "RiotAPIRequestFactory":

        parameter_iterable: Iterable[dict] 

        if "parameter_iterable" in kwargs:
            parameter_iterable = kwargs["parameter_iterable"]
            if not isinstance(parameter_iterable, Iterable):
                raise ValueError("parameter_iterable must be an iterable of dicts")
            elif isinstance(parameter_iterable, Generator):
                pass
            elif len(parameter_iterable) == 0:
                return None
            
        else:
            parameter_iterable = []
            parameter_dict = {}
            for argument, value in kwargs.items():
                if argument == "region":
                    continue
                parameter_dict[argument] = value
                
            parameter_iterable.append(parameter_dict)

        if "region" not in kwargs:
            raise ValueError("Missing region argument.")

        region = kwargs["region"]

        def url_factory(region=region, **kwargs):
            return base_url.format(region=region, **kwargs)
        
        if not isinstance(parameter_iterable, Iterator):
            parameter_iterable = iter(parameter_iterable)

        return cls(region, parameter_iterable, url_factory)


    def __iter__(self):
        return self
    

    def __next__(self):
         
        try:
            parameters: dict = next(self.parameter_iterable)
            url: str
            url = self.url_factory(
                self.region,
                **parameters
            )
            return url
        
        except KeyError as e:
            raise ValueError(f"Parameter missing value for {e}") 
        
        


class ResultsFactory():
    def __init__(self, 
        request_factory: RiotAPIRequestFactory, 
        session: ClientSession,
        rate_limiter: BaseRateLimiter
        ):
        self.request_factory : Final[RiotAPIRequestFactory] = request_factory
        self.session : Final[ClientSession] =  session
        self.rate_limiter : Final[BaseRateLimiter] = rate_limiter
        
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        
        try:
            url = next(self.request_factory)
        
            async with self.session.get(url=url, middlewares=[self.rate_limiter]) as resp:
                text = await resp.text()
                return text
        
        except StopIteration:
            raise StopAsyncIteration



if __name__ == "__main__":

    options = {
        "queue" : "SOLO", 
        "tier": "DIAMOND",
        "division" : "I",
        "page" : 1
        }
    parameter_iterable = [options for _ in range(5)]

    def url_factory(
        region,
        queue,
        tier,
        division,
        page  
    ):
        return f"https://{region}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}?page={page}"

    # request_factory = Request_factory(region="euw1", url_factory=url_factory, parameter_iterable=parameter_iterable)

    # for url in request_factory:
    #     print(url)

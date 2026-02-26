from functools import wraps
from inspect import signature


def handle_request(url, **kwargs):
    print("url", url)
    for argument, value in kwargs.items():
        print(argument, value)


def riot_api_endpoint(base_url: str):
    def decorator(func):
        sig = signature(func)

        @wraps(func)
        def wrapper(**kwargs):
        
            def url_builder(**builder_kwargs):
                return base_url.format(**builder_kwargs)
                

            # url = base_url.format(**kwargs)
            # return url
            return url_builder
        return wrapper
    return decorator


@riot_api_endpoint("https://{region}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}?page={page}")
def get_league_v4_entries_queue_tier_division(
    *,
    region,
    queue,
    tier,
    division,
    page,
    parameter_iterable
    
):
    ...
    
    # def url_contructor(
    #     region,
    #     queue,
    #     tier,
    #     division,
    #     page  
    # ):
    #     return f"https://{region}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}?page={page}"
    
    # return handle_request(
    #     url=url_contructor, region=region, queue=queue, tier=tier, division=division, page=page, options=options
    # )


if __name__ == "__main__":

    val = get_league_v4_entries_queue_tier_division(
        region="euw1",
        queue="SOLO",
        tier="DIAMOND",
        division="I",
        page=1,
        parameter_iterable=None
    )


    a= {
        "region":"euw1",
        "queue":"SOLO",
        "tier":"DIAMOND",
        "division":"I",
        "page":1,
        "parameter_iterable": None
    }
    url = val(**a)
    print(url)
    # 'euw1', 'SOLO', 'DIAMOND', 'I', 1
    # base = "https://{region}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}?page={page}"
    # args = {
    #     "region" : "euw1",
    # }

    # def _(**args):
    #     print (*args)
    # # print(**args)
    # _(**args)
    # base.format(**args)
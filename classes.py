import requests
import asyncio

# "https://{region}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}"


def handle_request(url, method='get', **kwargs):
    try:
        response = getattr(requests, method)(url, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
    return None


def get_league_v4_entries_by_queue_tier_division(
        region,
        queue,
        tier,
        division,
        page,
        api_key
):

    request_params = {
        'api_key' : api_key,
        'page' : page 
    }
    request_url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}"
    response = handle_request(url=request_url, method='get', params=request_params)
    return response.json()

async def get_league_v4_entries_by_queue_tier_division_pages(
        pages: int,
        region: str, 
        queue : str = "RANKED_SOLO_5x5", 
        tier: str = "CHALLENGER", 
        division: str = "I"
    ):

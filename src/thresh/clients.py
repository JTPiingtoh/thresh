from abc import ABC, abstractmethod
from sources import RiotAPI




# TODO: takes a pipleline from which to source and store data, eg cache, local, api
class RiotAPIClient():


    def __init__(self):
        self.rate_limiter = ... # this needs to be a rate limiter global to thresh


    async def get_league_matches_exp_v4_by_queue_tier_division(
            self,
            region,
            page,
            queue,
            tier,
            division
            ):
        return await self.get(f"https://{region}.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={page}")
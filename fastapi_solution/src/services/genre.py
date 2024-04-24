from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.base import BaseService



class GenreService(BaseService):

    async def get_genres(self,
                         request_url: str,
                         model: Genre,
                         index: str) -> list[Genre]:
        doc = await self.get_many(request_url=request_url, model=model, method=self.elastic.search,
                                  index=index, size=1000)
        return doc


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)

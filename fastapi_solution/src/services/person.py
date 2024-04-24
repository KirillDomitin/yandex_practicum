from functools import lru_cache
import logging

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from services.base import BaseService


class PersonService(BaseService):

    async def search_persons(self,
                             request_url: str,
                             model: Person,
                             index: str,
                             query_string: str,
                             page: int,
                             page_size: int, ) -> list[Person] | None:
        body = {
            'from': (page - 1) * page_size,
            'size': page_size,
            'query': {'query_string': {'query': query_string}},
            'sort': [{'_score': 'desc'}],
        }
        logging.info(f"at PersonService: \n{body}")
        doc = await self.get_many(request_url=request_url, model=model, method=self.elastic.search,
                                  index=index, body=body)
        return doc


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)

from functools import lru_cache
import logging
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import FilmShort
from services.base import BaseService


class FilmService(BaseService):

    async def search_films(self,
                           request_url: str,
                           model: FilmShort,
                           index: str,
                           query_string: str,
                           page: int,
                           page_size: int, ) -> list[FilmShort]:
        body = {
            '_source': list(model.schema()['properties'].keys()),
            'from': (page - 1) * page_size,
            'size': page_size,
            'query': {'query_string': {'query': query_string}},
            'sort': [{'_score': 'desc'}],
        }
        doc = await self.get_many(request_url=request_url, model=model, method=self.elastic.search,
                                  index=index, body=body)
        return doc

    async def get_films_by_filter(self,
                                  request_url: str,
                                  model: FilmShort,
                                  index: str,
                                  page: int,
                                  page_size: int,
                                  sort_by: str,
                                  sort_order: str,
                                  genre: UUID,
                                  director: UUID,
                                  writer: UUID,
                                  actor: UUID, ) -> list[FilmShort]:
        _filters = [i for i in [
            {'nested': {'path': 'genres', 'query': {'match': {'genres.id': genre}}}} if genre else None,
            {'nested': {'path': 'directors', 'query': {'match': {'directors.id': director}}}} if director else None,
            {'nested': {'path': 'writers', 'query': {'match': {'writers.id': writer}}}} if writer else None,
            {'nested': {'path': 'actors', 'query': {'match': {'actors.id': actor}}}} if actor else None,
        ] if i]
        body = {
            "_source": list(model.schema()['properties'].keys()),
            'from': (page - 1) * page_size,
            'size': page_size,
            'query': {'bool': {'must': _filters}},
            'sort': [{sort_by: sort_order}],
        }
        logging.info(f"at get_films_by_filter: \n{body}")
        doc = await self.get_many(request_url=request_url, model=model, method=self.elastic.search,
                                  index=index, body=body)
        return doc


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)

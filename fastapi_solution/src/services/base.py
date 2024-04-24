import logging
import json
from typing import Callable, TypeAlias

from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch
from pydantic import TypeAdapter
from redis.asyncio import Redis

from core.config import REDIS_CACHE_EXPIRE_IN_SECONDS
from models.film import Film, FilmShort
from models.genre import Genre
from models.person import Person

ModelsTypes: TypeAlias = [Film | FilmShort | Genre | Person]
ModelsTypesOptional: TypeAlias = [Film | FilmShort | Genre | Person | None]


class BaseService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def _get_from_cache(self, key: str) -> list | dict | None:
        data = await self.redis.get(key)
        if not data:
            return None
        data = json.loads(data)
        return data

    async def _put_to_cache(self, key: str, doc: list | dict) -> None:
        await self.redis.set(key, json.dumps(doc), REDIS_CACHE_EXPIRE_IN_SECONDS)

    async def get_by_id(self,
                        request_url: str,
                        _id: str,
                        index: str,
                        model: ModelsTypes) -> ModelsTypesOptional:
        doc = await self._get_from_cache(key=request_url)
        if not doc:
            doc = await self.elastic.get(index=index, id=_id)
            if not doc:
                return None
            logging.info(f"______________ at get_by_id: \n{doc}")
            doc = doc['_source']
            await self._put_to_cache(key=request_url, doc=doc)
        return TypeAdapter(model).validate_python(doc)

    async def get_many(self,
                       request_url: str,
                       model: ModelsTypes,
                       method: Callable[[...], ObjectApiResponse],
                       **params) -> ModelsTypesOptional:
        doc = await self._get_from_cache(key=request_url)
        if not doc:
            doc = await method(**params)
            if not doc:
                return None
            if not doc.get('hits').get('hits'):
                return None
            logging.info(f"______________ at get_many: \n{doc}")
            doc = [el['_source'] for el in doc['hits']['hits']]
            await self._put_to_cache(key=request_url, doc=doc)
        return TypeAdapter(list[model]).validate_python(doc)


import datetime
import os
import uuid

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from .settings import test_settings

ELASTIC_HOST = os.getenv("ELASTIC_HOST", "localhost")
ELASTIC_PORT = os.getenv("ELASTIC_PORT", 9200)


#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий.

@pytest.mark.asyncio
async def test_search():
    # 1. Генерируем данные для ES
    es_data = [{
        "id": "2a090dde-f688-46fe-a9f4-b781a985275e",
        "title": "Star Wars: Knights of the Old Republic",
        "imdb_rating": 9.6,
        "description": "Four thousand years before the fall of the Republic, before the fall of the Jedi, a great war was fought, between the armies of the Sith and the forces of the Republic. A warrior is chosen to rescue a Jedi with a power important to the cause of the Republic, but in the end, will the warrior fight for the Light Side of the Force, or succumb to the Darkness?",
        "directors": [
            {
                "id": "1a9e7e1f-393b-455d-a76f-d3ad2b33673e",
                "full_name": "Casey Hudson"
            }
        ],
        "actors": [
            {
                "id": "bccbbbb6-be40-44f5-a025-204bcfcf2667",
                "full_name": "Raphael Sbarge"
            }
        ],
        "writers": [
            {
                "id": "8778550c-90c6-4180-a6ac-eba956f0ce59",
                "full_name": "David Gaider"
            }
        ],
        "genres": [
            {
                "id": "b92ef010-5e4c-4fd0-99d6-41b6456272cd",
                "name": "Fantasy"
            }
        ],
        "directors_names": [
            "Casey Hudson"
        ],
        "writers_names": [
            "David Gaider"
        ],
        "actors_names": [
            "Raphael Sbarge"
        ]
    } for _ in range(60)]

    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': 'movies', '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    # 2. Загружаем данные в ES
    es_client = AsyncElasticsearch(
        hosts=f"http://{ELASTIC_HOST}:{ELASTIC_PORT}", verify_certs=False)
    if await es_client.indices.exists(index=test_settings.es_index):
        await es_client.indices.delete(index=test_settings.es_index)
    await es_client.indices.create(index=test_settings.es_index, **test_settings.es_index_mapping)
    updated, errors = await async_bulk(client=es_client, actions=bulk_query)
    print('updated', updated)
    print('errors', errors)
    doc = {
        'query': {
            'match_all': {}
        }
    }
    res = await es_client.search(index='movies',body=doc,size=20)
    # res = await es_client.indices.get_alias(index="*")
    print(res)
    await es_client.close()

    if errors:
        raise Exception('Ошибка записи данных в Elasticsearch')

    # 3. Запрашиваем данные из ES по API

    timeout = aiohttp.ClientTimeout(total=60)
    session = aiohttp.ClientSession(trust_env=True, timeout=timeout)
    url = test_settings.service_url + '/api/v1/films/search'
    # http://localhost/api/v1/films/search?query_string=star&page=1&page_size=10
    query_data = {
        'query_string': 'Star',
        'page': 1,
        'page_size': 10
    }
    print('url', url)
    async with session.get(url, params=query_data, ssl=False) as response:
        body = await response.json()
        headers = response.headers
        status = response.status
    await session.close()

    # 4. Проверяем ответ

    assert status == 200
    assert len(body) == 50

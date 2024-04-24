from pydantic import Field
from pydantic_settings import BaseSettings

from testdata.mapping import MAPPING


class TestSettings(BaseSettings):
    es_host: str = 'http://elastic_test:9200'
    es_index: str = 'movies'
    # es_id_field: str = ...
    es_index_mapping: dict = MAPPING

    redis_host: str = Field('redis_test', env='REDIS_HOST')
    service_url: str = Field('http://fastapi_test:8000', env='FASTAPI_HOST')
    # service_url: str = Field('http://fastapi_test', env='FASTAPI_HOST')


test_settings = TestSettings()



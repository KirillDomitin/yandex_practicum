import os
from logging import config as logging_config

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from core.logger import LOGGING


class RedisModel(BaseModel):
    host: str = os.environ.get('REDIS_HOST')
    port: int = int(os.environ.get('REDIS_PORT'))


class ESModel(BaseModel):
    host: str = os.environ.get('ES_HOST')
    port: int = int(os.environ.get('ES_PORT'))


class FastApiModel(BaseModel):
    host: str = os.environ.get('FASTAPI_HOST')
    port: int = int(os.environ.get('FASTAPI_PORT'))


class Settings(BaseSettings):
    redis: RedisModel = RedisModel()
    elasticsearch: ESModel = ESModel()
    fastapi: FastApiModel = FastApiModel()


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')


# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


REDIS_CACHE_EXPIRE_IN_SECONDS = 60 * 5

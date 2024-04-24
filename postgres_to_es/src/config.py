import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class EsOpts(BaseModel):
    es_host: str = os.environ.get('ES_HOST')
    es_port: str = os.environ.get('ES_PORT')


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    postgresql_opts: str = f"dbname={os.environ.get('PG_NAME')} " \
                           f"user={os.environ.get('PG_USER')} " \
                           f"password={os.environ.get('PG_PASSWORD')} " \
                           f"host={os.environ.get('PG_HOST')} " \
                           f"port={os.environ.get('PG_PORT')} "

    es_opts: EsOpts = EsOpts()
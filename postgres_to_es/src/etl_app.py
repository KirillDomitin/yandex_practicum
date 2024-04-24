import io
import json
import logging
import os
import time
from contextlib import contextmanager
from functools import wraps
from pathlib import Path

import psycopg2
from psycopg2.extras import DictCursor
import requests

from src.config import Settings


ELASTIC_SEARCH_INDEXES_PATH = Path(Path(__file__).resolve().parent, 'resources/elasticsearch_indexes')
POSTGRESQL_DDL_PATH = Path(Path(__file__).resolve().parent, 'resources/postgresql_ddls')


@contextmanager
def postgresql_conn():
    """
    Менеджер контекста для подключения Postgresql.
    """
    opts = Settings().model_dump()['postgresql_opts']
    connection = psycopg2.connect(opts)
    try:
        yield connection
    finally:
        connection.close()


def backoff(start_sleep_time=1, factor=2, border_sleep_time=100):
    """Декоратор для ретраев"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _try = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.error('___________ BACKOFF WRAPPER ___________', exc_info=e)
                    _try += 1
                    delay = start_sleep_time * (factor ** _try)
                    delay = delay if delay < border_sleep_time else border_sleep_time
                    time.sleep(delay)

        return wrapper

    return decorator


class JsonFileStorage:
    def __init__(self, file_path):
        self.file_path = file_path
        self.state = {}
        self.get_state()

    def save_state(self):
        """Сохранить состояние в файл."""
        with open(self.file_path, mode='w') as f:
            f.write(json.dumps(self.state))

    def get_state(self):
        """Загрузить состояние из файла."""
        if os.path.isfile(self.file_path):
            with open(self.file_path) as f:
                self.state = json.loads(f.read())
        else:
            for idx in [f.replace('.json', '') for f in os.listdir(ELASTIC_SEARCH_INDEXES_PATH)]:
                self.state[idx] = '2021-01-01 00:00:00.000000 +0300'
            with open(self.file_path, mode='x') as f:
                f.write(json.dumps(self.state))
            logging.info(f'Created JsonFileStorage: {self.state}')


class ETL:
    def __init__(self, storage):
        self.es_host = Settings().model_dump()['es_opts']['es_host']
        self.es_port = Settings().model_dump()['es_opts']['es_port']
        self.url = f'http://{self.es_host}:{self.es_port}'
        self.headers = {'Content-Type': 'application/json'}
        self.storage = storage

    def transfer_data(self, pg_conn):
        pg_cursor = pg_conn.cursor(cursor_factory=DictCursor)
        self.storage.get_state()
        ddl_dict = {f.replace('.ddl', ''): f for f in os.listdir(POSTGRESQL_DDL_PATH)}
        for idx in ddl_dict:
            with open(Path(POSTGRESQL_DDL_PATH, f'{idx}.ddl')) as f:
                query = f.read()
            pg_cursor.execute(query.format(**self.storage.state))

            while batch := pg_cursor.fetchmany(100):
                data = io.StringIO()
                for row in batch:
                    row = dict(row)
                    self.storage.state[idx] = row.pop('modified')
                    data.write(json.dumps({"index": {"_index": idx, "_id": row['id']}}))
                    data.write('\n')
                    data.write(json.dumps(row))
                    data.write('\n')
                data.seek(0)
                data = data.read()

                url = self.url + '/_bulk?filter_path=items.*.error'
                r_json = requests.post(url=url, headers=self.headers, data=data).json()
                if r_json:
                    logging.info(r_json)
                    raise Exception(idx)
                else:
                    self.storage.save_state()
                    logging.info(f"ETL completed {self.storage.state}. Count rows: {len(batch)}")
                    time.sleep(0.3)

    @backoff()
    def start(self):
        with postgresql_conn() as pg_conn:
            while True:
                _aliases = requests.get(self.url+'/_aliases').json()
                indexes_dict = {f.replace('.json', ''): f for f in os.listdir(ELASTIC_SEARCH_INDEXES_PATH)}
                if _aliases.keys() == indexes_dict.keys():
                    self.transfer_data(pg_conn)
                    time.sleep(3)
                else:
                    for idx in indexes_dict:
                        if idx not in _aliases:
                            with open(Path(ELASTIC_SEARCH_INDEXES_PATH, indexes_dict[idx])) as f:
                                index = json.dumps(json.loads(f.read()))
                            r_json = requests.put(url=self.url+f'/{idx}', headers=self.headers, data=index).json()
                            logging.info(f'Putting elasticsearch schema. Response json: {r_json}')

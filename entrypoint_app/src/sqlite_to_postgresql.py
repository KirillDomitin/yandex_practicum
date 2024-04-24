import io
import os
from contextlib import contextmanager
from pathlib import Path
from functools import wraps
import time
import logging

import sqlite3
import psycopg2
from psycopg2.extensions import connection as _connection


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
                    logging.error(e)
                    _try += 1
                    delay = start_sleep_time * (factor ** _try)
                    delay = delay if delay < border_sleep_time else border_sleep_time
                    time.sleep(delay)
        return wrapper
    return decorator


@contextmanager
def sqlite_conn() -> sqlite3.Connection:
    """
    Менеджер контекста для подключения SQLite.
    """
    connection = sqlite3.connect(Path(Path(__file__).resolve().parent, 'resources/db.sqlite'))

    def str_factory(cursor, row):
        return '\t'.join([str(el) for el in row])  # кастомный row_factory - возвращает строки в формате csv

    connection.row_factory = str_factory
    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def postgresql_conn() -> _connection:
    """
    Менеджер контекста для подключения Postgresql.
    """
    params = {
        'dbname': os.environ.get('PG_NAME'),
        'user': os.environ.get('PG_USER'),
        'password': os.environ.get('PG_PASSWORD'),
        'host': os.environ.get('PG_HOST'),
        'port': os.environ.get('PG_PORT'),
    }
    connection = psycopg2.connect(**params)
    try:
        yield connection
    finally:
        connection.close()


def parse_sqlite_ddl() -> dict:
    """
    Парсим ddl file.
    Возвращает словарь, где ключи - названия таблиц, а значения - запрос к этим таблицам в SQLite.
    """
    with open(Path(Path(__file__).resolve().parent, 'resources/SQLite_table_prepair.ddl')) as f:
        res = f.read()
    return {
        el.split('---')[0].replace('-', '').strip(): el.split('---')[1].replace('-', '').strip()
        for el in res.split('----')
    }


def do_transactions(sqlite3_connection: sqlite3.Connection, pg_connection: _connection, tables: dict) -> None:
    """
    Основная функция.
    """
    with sqlite3_connection as sl_conn, pg_connection as pg_conn:  # подключаемся и создаём курсоры
        sl_cursor = sl_conn.cursor()
        pg_cursor = pg_conn.cursor()
        with open(Path(Path(__file__).resolve().parent, 'resources/content_schema.ddl')) as f:
            pg_cursor.execute(f.read())

        for tbl in tables.keys():  # проходимся по табилцам
            logging.info(f"{tbl} executing starts")
            sl_cursor.execute(tables[tbl])  # select'им из них данные
            columns = ','.join([el[0] for el in sl_cursor.description])  # отдельно сразу достаём названия колонок
            logging.info(f"{tbl} executing sqlite completed without errors")

            while batch := sl_cursor.fetchmany(10000):
                res = io.StringIO()  # сразу собираем из батча csv
                for row in batch:  # в таком варианте не нужно объявлять dataclasses + это самый быстрый способ
                    res.write(row)
                    res.write('\n')
                res.seek(0)

                pg_cursor.copy_expert(f"""
                                        COPY content.{tbl} ({columns})
                                        FROM STDIN
                                        WITH NULL 'None';
                                        COMMIT;
                                        """, res)  # заливаем батч через COPY
            logging.info(f"{tbl} executing ended without errors")


@backoff()
def load_data():
    do_transactions(sqlite_conn(),
                    postgresql_conn(),
                    parse_sqlite_ddl(), )

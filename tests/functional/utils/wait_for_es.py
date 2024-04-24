import os
import time

from elasticsearch import Elasticsearch

ELASTIC_HOST = os.getenv("ELASTIC_HOST", "localhost")
ELASTIC_PORT = os.getenv("ELASTIC_PORT", 9200)

if __name__ == '__main__':
    es_client = Elasticsearch(
        hosts=f"http://{ELASTIC_HOST}:{ELASTIC_PORT}")
    while True:
        is_running = es_client.ping()
        if is_running:
            break
        time.sleep(1)

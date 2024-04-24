import os
import time
from redis.asyncio import Redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 1)


async def wait_running():
    r = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    while True:
        is_running = r.ping()
        if is_running:
            yield r
            break
        time.sleep(1)


if __name__ == '__main__':
    wait_running()

import redis.asyncio as redis
import logging
import asyncio
from app.core.config import settings

logger = logging.getLogger(__name__)

class InMemoryCache:
    def __init__(self):
        self._data = {}
    async def get(self, key): return self._data.get(key)
    async def setex(self, key, ttl, value): self._data[key] = value
    async def incr(self, key):
        self._data[key] = int(self._data.get(key, 0)) + 1
        return self._data[key]
    async def ping(self): return True

redis_client = None

async def get_redis():
    global redis_client
    if redis_client is None:
        try:
            client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=1
            )
            await client.ping()
            redis_client = client
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis unavailable, using In-Memory cache: {e}")
            redis_client = InMemoryCache()
    return redis_client

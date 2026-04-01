import json
from typing import Any, Optional
import redis.asyncio as redis
from app.core.config import settings

redis_client: Optional[redis.Redis] = None

async def init_redis():
    global redis_client
    if settings.REDIS_URL:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.aclose()

async def get_cache(key: str) -> Optional[Any]:
    if not redis_client:
        return None
    data = await redis_client.get(key)
    if data:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data
    return None

async def set_cache(key: str, value: Any, expire: int = 3600):
    if not redis_client:
        return
    data = json.dumps(value) if isinstance(value, (dict, list)) else value
    await redis_client.set(key, data, ex=expire)

async def delete_cache(key: str):
    if not redis_client:
        return
    await redis_client.delete(key)

async def delete_cache_pattern(pattern: str):
    if not redis_client:
        return
    cursor = b'0'
    while cursor:
        cursor, keys = await redis_client.scan(cursor=cursor, match=pattern, count=100)
        if keys:
            await redis_client.delete(*keys)

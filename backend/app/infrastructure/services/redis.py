import redis
from app.config import settings

def get_redis_client():
    """Get Redis client with the current settings URL"""
    return redis.Redis.from_url(
        settings.REDIS_URL, 
        decode_responses=True
    )

# Get initial client
redis_client = get_redis_client()

def get_cache(key: str) -> str:
    return redis_client.get(key)

def set_cache(key: str, value: str, expiry: int = 3600) -> bool:
    return redis_client.set(key, value, ex=expiry)

def delete_cache(key: str) -> int:
    return redis_client.delete(key)

def get_cache_keys(pattern: str) -> list:
    return redis_client.keys(pattern)

def clear_cache_by_pattern(pattern: str) -> int:
    keys = get_cache_keys(pattern)
    if keys:
        return redis_client.delete(*keys)
    return 0 
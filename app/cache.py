# cache.py
from cachetools import TTLCache

# Small in-memory cache for testing/scaffold
query_cache = TTLCache(maxsize=1024, ttl=300)

def get_cache(key: str):
    return query_cache.get(key)

def set_cache(key: str, value):
    query_cache[key] = value


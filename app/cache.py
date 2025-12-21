# cach.py

_cache = {}

def get_cache(key):
    """Return cached value for a key, or None if not present."""
    return _cache.get(key)

def set_cache(key, value):
    """Set a value in the cache."""
    _cache[key] = value

def clear_cache():
    global _cache
    _cache = {}

import redis
from datetime import datetime

class RedisService:
    def __init__(self, redis_client: redis.Redis):
        self.client = redis_client

    # --- string ---
    def set_string(self, key: str, value: str, ttl: int = None):
        if ttl is not None:
            self.client.setex(key, ttl, value)
        else:
            self.client.set(key, value)

    def get_string(self, key: str):
        return self.client.get(key)

    def delete_key(self, key: str):
        self.client.delete(key)

    def increment(self, key: str, amount: int = 1):
        return self.client.incrby(key, amount)

    # --- list ---
    def list_push(self, key: str, value: str, left: bool = True):
        if left:
            self.client.lpush(key, value)
        else:
            self.client.rpush(key, value)

    def list_range(self, key: str, start: int, end: int):
        return self.client.lrange(key, start, end)

    def list_pop(self, key: str, left: bool = True):
        if left:
            return self.client.lpop(key)
        else:
            return self.client.rpop(key)

    # --- hash ---
    def hash_set(self, key: str, field: str, value: str):
        self.client.hset(key, field, value)

    def hash_get(self, key: str, field: str):
        return self.client.hget(key, field)

    def hash_get_all(self, key: str):
        return self.client.hgetall(key)

    def hash_delete(self, key: str, field: str):
        self.client.hdel(key, field)

    # --- TTL ---
    def expire(self, key: str, ttl: int):
        self.client.expire(key, ttl)

    def ttl(self, key: str):
        return self.client.ttl(key)

    # --- для заметок: кэш и мета ---
    def cache_note(self, note_id: int, content: str, ttl: int = 3600):
        self.client.setex(f"note:{note_id}:content", ttl, content)

    def get_cached_note(self, note_id: int):
        return self.client.get(f"note:{note_id}:content")

    def delete_cached_note(self, note_id: int):
        self.client.delete(f"note:{note_id}:content")

    def set_note_meta(self, note_id: int, field: str, value: str):
        self.client.hset(f"note:{note_id}:meta", field, value)

    def get_note_meta(self, note_id: int):
        return self.client.hgetall(f"note:{note_id}:meta")

    def delete_note_meta(self, note_id: int):
        self.client.delete(f"note:{note_id}:meta")
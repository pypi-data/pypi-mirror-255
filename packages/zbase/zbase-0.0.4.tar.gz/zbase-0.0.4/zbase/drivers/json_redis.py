import redis
import json
from ..utils.jsons import dumps
from typing import Any

class RedisJSON():

    def __init__(self, redis: redis.Redis):
        self.redis = redis

    def set(self, key: str, value: dict , ex: int = None):
        self.redis.set(key, dumps(value),ex=ex)

    def get(self, key: str)->Any:
        return json.loads(self.redis.get(key))
    
    def mset(self, mapping: dict, ex: int = None):
        self.redis.mset({k: dumps(v) for k, v in mapping.items()})
        if ex:
            for k in mapping.keys():
                self.redis.expire(k, ex)
    
    def mget(self, keys: list)->dict:
        return {k: json.loads(v) for k, v in self.redis.mget(keys).items()}
    
    def hset(self, name: str, key: str, value: dict , ex: int = None):
        self.redis.hset(name, key, dumps(value))
        if ex:
            self.redis.expire(name, ex)
    
    def hsetall(self, name: str, mapping: dict , ex: int = None):
        self.redis.hset(name, {k: dumps(v) for k, v in mapping.items()})
        if ex:
            self.redis.expire(name, ex)
    
    def hget(self, name: str, key: str)->Any:
        return json.loads(self.redis.hget(name, key))
    
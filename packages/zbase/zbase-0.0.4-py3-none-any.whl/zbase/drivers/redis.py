import redis
from ..env import getEnv,getEnvInt

redisPoolEnv = redis.ConnectionPool(host=getEnv('REDIS_HOST','localhost'), port=getEnvInt('REDIS_PORT',6379), db=getEnvInt('REDIS_DB',0))

def newRedisEnv()->redis.Redis:
    return redis.Redis(connection_pool=redisPoolEnv)

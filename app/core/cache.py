# app/core/cache.py
import os
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis
from fastapi import FastAPI

async def init_cache(app: FastAPI):
    # redis = Redis(host="redis", port=6379, db=0, decode_responses=True)
    # 动态获取 Redis Host，默认为 "redis"（照顾你本地的 docker-compose）
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis = Redis(host=redis_host, port=6379, db=0, decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="policy-api")
    app.state.redis = redis
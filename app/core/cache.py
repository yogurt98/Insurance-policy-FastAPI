# app/core/cache.py
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis
from fastapi import FastAPI

async def init_cache(app: FastAPI):
    redis = Redis(host="redis", port=6379, db=0, decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="policy-api")
    app.state.redis = redis
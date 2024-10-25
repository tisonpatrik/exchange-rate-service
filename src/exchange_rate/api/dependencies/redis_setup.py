from contextlib import asynccontextmanager
from functools import lru_cache

import redis.asyncio as redis
from fastapi import FastAPI

from exchange_rate.logging.logger import AppLogger

logger = AppLogger.get_instance().get_logger()


@lru_cache
@asynccontextmanager
async def setup_async_redis(app: FastAPI):
    try:
        pool = redis.ConnectionPool.from_url("redis://redis:6379")
        app.state.redis_pool = pool
        logger.info("Redis connection pool initialized successfully.")
        yield
    except redis.ConnectionError:
        logger.exception("Failed to initialize Redis connection pool: ")
        raise
    finally:
        await app.state.redis_pool.aclose()  # type: ignore
        logger.info("Redis connection pool closed successfully.")

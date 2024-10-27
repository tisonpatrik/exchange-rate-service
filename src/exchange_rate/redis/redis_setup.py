from contextlib import asynccontextmanager
from functools import lru_cache

import redis.asyncio as redis
from fastapi import FastAPI
from redis.exceptions import TimeoutError

from exchange_rate.config import config
from exchange_rate.logging.logger import AppLogger

logger = AppLogger.get_instance().get_logger()


@lru_cache
@asynccontextmanager
async def setup_async_redis(app: FastAPI):
    try:
        pool = redis.ConnectionPool.from_url(
            url=config.REDIS_URL,
            max_connections=config.MAX_REDIS_CONNECTIONS,
            socket_timeout=config.REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=config.REDIS_SOCKET_CONNECT_TIMEOUT,
            retry_on_timeout=True,
        )
        app.state.redis_pool = pool
        logger.info("Redis connection pool initialized successfully.")
        yield
    except ConnectionError as e:
        logger.exception(
            "Failed to initialize Redis connection pool due to connection error"
        )
        raise e
    except TimeoutError as e:
        logger.exception("Redis connection pool initialization timed out")
        raise e
    finally:
        if app.state.redis_pool:
            await app.state.redis_pool.aclose()
            logger.info("Redis connection pool closed successfully.")

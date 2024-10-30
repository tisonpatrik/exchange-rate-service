from contextlib import asynccontextmanager
from functools import lru_cache

import redis.asyncio as redis
from exchange_rate.config import config
from exchange_rate.logging.logger import AppLogger
from redis.exceptions import TimeoutError

logger = AppLogger.get_instance().get_logger()


@lru_cache
@asynccontextmanager
async def setup_async_redis():
    pool = None
    try:
        pool = redis.ConnectionPool.from_url(
            url=config.REDIS_URL,
            max_connections=config.MAX_REDIS_CONNECTIONS,
            socket_timeout=config.REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=config.REDIS_SOCKET_CONNECT_TIMEOUT,
            retry_on_timeout=True,
        )
        logger.info("Redis connection pool initialized successfully.")
        yield pool
    except ConnectionError:
        logger.exception("Failed to initialize Redis connection pool due to connection error")
        raise
    except TimeoutError:
        logger.exception("Redis connection pool initialization timed out")
        raise
    finally:
        if pool:
            await pool.aclose()
            logger.info("Redis connection pool closed successfully.")

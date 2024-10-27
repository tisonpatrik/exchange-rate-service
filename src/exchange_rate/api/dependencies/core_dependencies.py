import asyncio
from contextlib import asynccontextmanager
from functools import lru_cache

import redis.asyncio as redis
from fastapi import Depends, FastAPI, Request
from redis.exceptions import TimeoutError

from exchange_rate.api.handlers.conversion_handler import ConversionHandler
from exchange_rate.api.websocket.websocket_client import WebSocketClient
from exchange_rate.config import config
from exchange_rate.logging.logger import AppLogger
from exchange_rate.redis.redis_client import RedisClient

logger = AppLogger.get_instance().get_logger()


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    async with setup_async_redis(app), setup_websocket_client(app):
        yield


def get_redis(request: Request) -> RedisClient:
    return RedisClient(request.app.state.redis_pool)


def get_conversion_handler(
    redis_client: RedisClient = Depends(get_redis),
) -> ConversionHandler:
    return ConversionHandler(redis_client=redis_client)


@asynccontextmanager
async def setup_websocket_client(app):
    handler = get_conversion_handler()
    websocket_client = WebSocketClient(conversion_handler=handler)
    task = asyncio.create_task(websocket_client.connect())
    logger.info("WebSocket client initialized successfully.")

    try:
        yield
    finally:
        task.cancel()
        await task
        logger.info("WebSocket client connection closed.")


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

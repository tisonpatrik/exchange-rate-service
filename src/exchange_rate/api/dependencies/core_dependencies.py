import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from exchange_rate.api.handlers.conversion_handler import ConversionHandler
from exchange_rate.api.websocket.websocket_client import WebSocketClient
from exchange_rate.freecurrency.freecurrency_client import FreeCurrencyAPIClient
from exchange_rate.freecurrency.freecurrency_setup import (
    setup_freecurrencyapi_client,
)
from exchange_rate.logging.logger import AppLogger
from exchange_rate.redis.redis_client import RedisClient
from exchange_rate.redis.redis_setup import setup_async_redis

logger = AppLogger.get_instance().get_logger()


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Nastavení Redis a FreeCurrencyAPI klientů
    async with setup_async_redis(app), setup_freecurrencyapi_client(app):
        # Ručně inicializujeme Redis klienta a FreeCurrencyAPI klienta
        redis_client = RedisClient(app.state.redis_pool)
        freecurrency_client = FreeCurrencyAPIClient(app.state.currency_api_client)

        # Inicializujeme ConversionHandler s klienty
        handler = ConversionHandler(
            redis_client=redis_client, freecurrency_client=freecurrency_client
        )

        # Nastavíme WebSocket klienta s handlerem
        async with setup_websocket_client(app, handler):
            yield


@asynccontextmanager
async def setup_websocket_client(app: FastAPI, handler: ConversionHandler):
    websocket_client = WebSocketClient(conversion_handler=handler)
    task = asyncio.create_task(websocket_client.connect())
    logger.info("WebSocket client initialized successfully.")

    try:
        yield
    finally:
        task.cancel()
        await task
        logger.info("WebSocket client connection closed.")

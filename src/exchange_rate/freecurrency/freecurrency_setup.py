from contextlib import asynccontextmanager
from functools import lru_cache

from freecurrencyapi import Client

from exchange_rate.config import config
from exchange_rate.logging.logger import AppLogger

logger = AppLogger.get_instance().get_logger()


@lru_cache
@asynccontextmanager
async def setup_freecurrencyapi_client(app):
    try:
        client = Client(config.FREECURRENCYAPI_KEY)
        app.state.currency_api_client = client
        logger.info("Freecurrencyapi client initialized successfully.")
        yield
    except Exception as e:
        logger.exception("Failed to initialize Freecurrencyapi client: %s", e)
        raise e
    finally:
        # Pokud je potřeba další čištění, může být přidáno zde
        logger.info("Freecurrencyapi client setup completed.")

import asyncio
from asyncio import Task
from datetime import datetime

from freecurrencyapi import Client  # type: ignore

from exchange_rate.config import config
from exchange_rate.logging.logger import AppLogger
from exchange_rate.models.exchange_rates import GetExchangeRatesCache, SetExchangeRatesCache
from exchange_rate.models.models import LatestExchangeRatesResponse
from exchange_rate.redis.redis_client import RedisClient


class FreeCurrencyAPIClient:
    def __init__(self, redis_client: RedisClient):
        self.client = Client(config.FREECURRENCYAPI_KEY)
        self.redis_client = redis_client
        self.logger = AppLogger.get_instance().get_logger()
        self.background_tasks: set[Task] = set()

    async def get_latest_exchange_rates(self, base_currency: str) -> LatestExchangeRatesResponse:
        try:
            self.logger.info("Retrieving latest exchange rates for base currency %s", base_currency)
            cached_data = await self._get_cached_values(base_currency)
            if cached_data is not None:
                return LatestExchangeRatesResponse(last_updated_at=datetime.utcnow(), data=cached_data)
            result = self.client.latest(base_currency=base_currency)
            self._set_cache_data(result["data"], base_currency)
            return LatestExchangeRatesResponse(last_updated_at=datetime.utcnow(), data=result["data"])
        except Exception:
            self.logger.exception("Failed to retrieve latest exchange rates for base currency %s", base_currency)
            raise

    async def _get_cached_values(self, currency) -> dict | None:
        cache_statement = GetExchangeRatesCache(currency)
        cached_data = await self.redis_client.get_cache(cache_statement)
        if cached_data is not None:
            self.logger.info("Cache hit for asset class: %s", currency)
            return cached_data
        return None

    def _set_cache_data(self, data: dict, currency: str) -> None:
        cache_statement = SetExchangeRatesCache(data=data, currency=currency)
        cache_task = asyncio.create_task(self.redis_client.set_cache(cache_statement))
        self.background_tasks.add(cache_task)
        cache_task.add_done_callback(self.background_tasks.discard)

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from exchange_rate.api.dependencies.app_dependencies import (
    connect_to_currency_assignment,
)
from exchange_rate.api.handlers.conversion_handler import ConversionHandler
from exchange_rate.redis.redis_client import RedisRepository
from exchange_rate.redis.redis_setup import setup_async_redis


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    async with setup_async_redis(app):
        # Start background task for the WebSocket connection to currency-assignment
        task = asyncio.create_task(connect_to_currency_assignment())

        yield  # This allows FastAPI to continue setting up the application

        # Cleanup after application shutdown
        task.cancel()
        await task


def get_redis(request: Request) -> RedisRepository:
    return RedisRepository(request.app.state.redis_pool)


def get_conversion_handler() -> ConversionHandler:
    return ConversionHandler()

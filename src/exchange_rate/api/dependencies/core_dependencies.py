from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from exchange_rate.api.handlers.conversion_handler import ConversionHandler
from exchange_rate.redis.redis_client import RedisRepository
from exchange_rate.redis.redis_setup import setup_async_redis


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    async with setup_async_redis(app):
        yield


def get_redis(request: Request) -> RedisRepository:
    return RedisRepository(request.app.state.redis_pool)


def get_conversion_handler() -> ConversionHandler:
    return ConversionHandler()

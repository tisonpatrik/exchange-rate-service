import asyncio

from exchange_rate.api.handlers.conversion_handler import ConversionHandler
from exchange_rate.api.websocket.websocket_client import WebSocketClient
from exchange_rate.freecurrency.freecurrency_client import FreeCurrencyAPIClient
from exchange_rate.redis.redis_client import RedisClient
from exchange_rate.redis.redis_setup import setup_async_redis


async def main():
    async with setup_async_redis() as redis_pool:
        redis_client = RedisClient(redis_pool)
        freecurrency_client = FreeCurrencyAPIClient(redis_client)
        conversion_handler = ConversionHandler(freecurrency_client=freecurrency_client)
        websocket_client = WebSocketClient(conversion_handler=conversion_handler)

        await websocket_client.start()


if __name__ == "__main__":
    asyncio.run(main())

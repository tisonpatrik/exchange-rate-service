import asyncio
import json

import websockets

from exchange_rate.config import config
from exchange_rate.logging.logger import AppLogger

logger = AppLogger.get_instance().get_logger()


async def connect_to_currency_assignment():
    while True:
        try:
            # Connect to the currency-assignment WebSocket URL
            async with websockets.connect(config.CURRENCY_ASSIGNMENT_URL) as ws:
                logger.info("Connected to currency-assignment WebSocket.")

                while True:
                    try:
                        # Wait for messages with a timeout
                        message = await asyncio.wait_for(ws.recv(), timeout=1)
                        data = json.loads(message)
                        logger.info("Received message: %s", data)
                    except asyncio.TimeoutError:
                        logger.warning(
                            "No message received within 10 seconds. Listening continues..."
                        )
        except websockets.ConnectionClosed as e:
            logger.error("WebSocket connection closed: %s", e)
            await asyncio.sleep(1)  # Brief delay before reconnecting

import asyncio
import json

import websockets
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed

from exchange_rate.api.dependencies.core_dependencies import get_conversion_handler
from exchange_rate.api.handlers.conversion_handler import ConversionHandler
from exchange_rate.config import config
from exchange_rate.logging.logger import AppLogger

websocket_router = APIRouter()
logger = AppLogger.get_instance().get_logger()


async def send_heartbeat(ws):
    while True:
        try:
            await ws.send(json.dumps({"type": "heartbeat"}))
            await asyncio.sleep(1)  # Send heartbeat every second
        except ConnectionClosed:
            break  # Exit if connection is closed


@websocket_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, handler: ConversionHandler = Depends(get_conversion_handler)
):
    await websocket.accept()

    while True:
        try:
            async with websockets.connect(config.CURRENCY_ASSIGNMENT_URL) as ws:
                logger.info("Connected to currency-assignment WebSocket.")
                last_heartbeat = asyncio.get_event_loop().time()

                # Start a task to send heartbeat messages
                heartbeat_task = asyncio.create_task(send_heartbeat(ws))

                while True:
                    try:
                        # Receive messages with a 2-second timeout
                        message = await asyncio.wait_for(ws.recv(), timeout=2)
                        data = json.loads(message)
                        logger.info("Received message: %s", data)

                        # Reset heartbeat timer on receiving any message
                        last_heartbeat = asyncio.get_event_loop().time()

                        # Process conversion requests if not a heartbeat
                        if data.get("type") != "heartbeat":
                            print(data)

                    except asyncio.TimeoutError:
                        # Check if more than 2 seconds have passed since the last heartbeat
                        if asyncio.get_event_loop().time() - last_heartbeat > 2:
                            logger.warning(
                                "No heartbeat received in over 2 seconds. Reconnecting..."
                            )
                            break  # Exit inner loop to reconnect

        except (ConnectionClosed, WebSocketDisconnect) as e:
            logger.error("WebSocket connection closed: %s", e)

        # Cancel heartbeat task before reconnecting
        heartbeat_task.cancel()
        await asyncio.sleep(1)  # Short delay before attempting to reconnect

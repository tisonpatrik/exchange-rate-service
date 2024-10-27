import asyncio
import json

import websockets

from exchange_rate.config import HEARTBEAT_INTERVAL, HEARTBEAT_TIMEOUT, config
from exchange_rate.logging.logger import AppLogger
from exchange_rate.models.models import (
    ConversionRequestMessage,
    HeartbeatMessage,
)


class WebSocketClient:
    def __init__(self):
        self.url = config.CURRENCY_ASSIGNMENT_URL
        self.logger = AppLogger.get_instance().get_logger()

    async def connect(self):
        while True:
            try:
                async with websockets.connect(self.url) as ws:
                    self.logger.info("Connected to currency-assignment WebSocket.")
                    await asyncio.gather(self.listen(ws), self.send_heartbeat(ws))
            except websockets.ConnectionClosed as e:
                self.logger.error("WebSocket connection closed: %s", e)
                await asyncio.sleep(HEARTBEAT_INTERVAL)

    async def listen(self, ws):
        try:
            while True:
                message = await asyncio.wait_for(ws.recv(), timeout=HEARTBEAT_TIMEOUT)
                data = json.loads(message)
                self.logger.info("Received message: %s", data)

                if data["type"] == "heartbeat":
                    self.logger.info("Received heartbeat.")
                elif data["type"] == "message":
                    # Here you would handle conversion requests
                    request = ConversionRequestMessage.parse_obj(data)
                    await self.handle_conversion_request(request)
                else:
                    self.logger.warning("Unknown message type received.")
        except asyncio.TimeoutError:
            self.logger.warning(
                "No message received within %s seconds. Connection will be refreshed.",
                HEARTBEAT_TIMEOUT,
            )
            await ws.close()

    async def send_heartbeat(self, ws):
        while True:
            await ws.send(HeartbeatMessage(type="heartbeat").json())
            self.logger.info("Sent heartbeat.")
            await asyncio.sleep(HEARTBEAT_INTERVAL)

    async def handle_conversion_request(self, request: ConversionRequestMessage):
        # Process the conversion request here
        self.logger.info("Processing conversion request with ID %s", request.id)
        # If conversion succeeds, send a response
        # If conversion fails, send ConversionErrorMessage
        pass

import asyncio
import json

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from exchange_rate.api.handlers.conversion_handler import ConversionHandler
from exchange_rate.config import HEARTBEAT_INTERVAL, HEARTBEAT_TIMEOUT, config
from exchange_rate.logging.logger import AppLogger
from exchange_rate.models.models import ConversionRequestMessage, HeartbeatMessage


class WebSocketClient:
    def __init__(self, conversion_handler: ConversionHandler):
        self.conversion_handler = conversion_handler
        self.url = config.CURRENCY_ASSIGNMENT_URL
        self.logger = AppLogger.get_instance().get_logger()

    async def connect(self):
        while True:
            try:
                async with connect(self.url, max_queue=20) as ws:
                    self.logger.info("Connected to currency-assignment WebSocket.")
                    await asyncio.gather(self.listen(ws), self.send_heartbeat(ws))
            except ConnectionClosedOK:
                # Expected behavior, log as a warning
                self.logger.warning("WebSocket connection closed gracefully (1000 OK). Reconnecting...")
                await asyncio.sleep(HEARTBEAT_INTERVAL)
            except ConnectionClosedError:
                # Other unexpected disconnections
                self.logger.exception("WebSocket connection closed unexpectedly: {e}")
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
                    response = await self.conversion_handler.convert_to_base_currency_async(request)
                    # Send the response back through the WebSocket
                    await ws.send(response.json())
                    self.logger.info("Sent response: %s", response.json())
                else:
                    self.logger.warning("Unknown message type received.")
        except TimeoutError:
            self.logger.warning(
                "No message received within %s seconds. Connection will be refreshed.",
                HEARTBEAT_TIMEOUT,
            )
            await ws.close()

    async def send_heartbeat(self, ws):
        while True:
            try:
                await ws.send(HeartbeatMessage().json())
                self.logger.info("Sent heartbeat.")
                await asyncio.sleep(HEARTBEAT_INTERVAL)
            except ConnectionClosedOK:
                self.logger.info("Connection closed gracefully during heartbeat.")
                break
            except ConnectionClosedError:
                self.logger.warning("Connection error detected during heartbeat.")
                break

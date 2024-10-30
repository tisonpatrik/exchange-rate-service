import asyncio
import json

from websockets.asyncio.client import ClientConnection, connect
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

    async def start(self):
        """Manages the WebSocket connection lifecycle with reconnection logic."""
        while True:
            try:
                async with connect(self.url, max_queue=20, logger=self.logger) as ws:
                    self.logger.info("Connected to currency-assignment WebSocket.")
                    await asyncio.gather(self._listen(ws), self._send_heartbeat(ws))
            except ConnectionClosedOK:
                self.logger.warning("WebSocket connection closed gracefully (1000 OK). Reconnecting...")
            except ConnectionClosedError:
                self.logger.exception("Unexpected WebSocket disconnection")
            except Exception:
                self.logger.exception("Critical error in WebSocket connection")
            finally:
                await asyncio.sleep(HEARTBEAT_INTERVAL)

    async def _listen(self, ws: ClientConnection):
        """Handles incoming WebSocket messages and processes business logic."""
        try:
            while True:
                message = await asyncio.wait_for(ws.recv(), timeout=HEARTBEAT_TIMEOUT)
                data = json.loads(message)
                self.logger.info("Received message: %s", data)

                if data.get("type") == "heartbeat":
                    self.logger.info("Received heartbeat.")
                elif data.get("type") == "message":
                    request = ConversionRequestMessage.parse_obj(data)
                    await self._process_conversion_request(ws, request)
                else:
                    self.logger.warning("Unknown message type received.")
        except TimeoutError:
            self.logger.warning("No message received within timeout; reconnecting WebSocket.")
            await ws.close()
        except ConnectionClosedError:
            self.logger.warning("Connection error during listen; attempting reconnection.")
        except Exception:
            self.logger.exception("Unexpected error in listen task: %s")

    async def _process_conversion_request(self, ws: ClientConnection, request: ConversionRequestMessage):
        """Processes conversion requests and sends the response."""
        try:
            response = await self.conversion_handler.convert_to_base_currency_async(request)
            await ws.send(response.json())
            self.logger.info("Sent response: %s", response.json())
        except Exception:
            self.logger.exception("Error processing conversion request")

    async def _send_heartbeat(self, ws: ClientConnection):
        """Sends periodic heartbeats to keep the WebSocket connection alive."""
        try:
            while True:
                await ws.send(HeartbeatMessage().json())
                self.logger.info("Sent heartbeat.")
                await asyncio.sleep(HEARTBEAT_INTERVAL)
        except ConnectionClosedOK:
            self.logger.info("Connection closed gracefully during heartbeat.")
        except ConnectionClosedError as e:
            self.logger.warning("Connection error during heartbeat: %s", str(e))
        except Exception:
            self.logger.exception("Unexpected error in heartbeat task")

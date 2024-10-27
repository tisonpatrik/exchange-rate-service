import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from exchange_rate.api.dependencies.core_dependencies import get_conversion_handler
from exchange_rate.api.handlers.conversion_handler import ConversionHandler
from exchange_rate.logging.logger import AppLogger
from exchange_rate.models.models import (
    ConversionErrorMessage,
    ConversionRequestMessage,
    ConversionResponseMessage,
    HeartbeatMessage,
)
from exchange_rate.utils.parser import (
    parse,  # Assuming the parse function is in utils/parser.py
)

websocket_router = APIRouter()
logger = AppLogger.get_instance().get_logger()


@websocket_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, handler: ConversionHandler = Depends(get_conversion_handler)
):
    await websocket.accept()
    try:
        while True:
            raw_data = await asyncio.wait_for(websocket.receive_json(), timeout=2)

            # Use the parse function to handle message validation and type checking
            message, success = parse(raw_data)

            if not success:
                await websocket.send_json(message.dict())
                continue

            # Process message based on parsed type
            if isinstance(message, HeartbeatMessage):
                await websocket.send_json(message.dict())
            elif isinstance(message, ConversionRequestMessage):
                try:
                    response_data = await handler.handle_conversion_request(
                        message.payload
                    )
                    response = ConversionResponseMessage(
                        type="message", id=message.id, payload=response_data
                    )
                    await websocket.send_json(response.dict())
                except Exception as e:
                    error_response = ConversionErrorMessage(
                        type="error",
                        id=message.id,
                        message=f"Unable to process request: {str(e)}",
                    )
                    await websocket.send_json(error_response.dict())

    except asyncio.TimeoutError:
        await websocket.close(code=1001, reason="No heartbeat received.")
        logger.info("Connection closed due to heartbeat timeout.")
    except WebSocketDisconnect:
        logger.info("Client disconnected.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await websocket.close(code=1011, reason="Server error.")

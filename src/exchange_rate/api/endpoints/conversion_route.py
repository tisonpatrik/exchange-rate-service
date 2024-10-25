import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.logger import logger

websocket_router = APIRouter()


@websocket_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await asyncio.wait_for(websocket.receive_json(), timeout=2)
            if data.get("type") == "heartbeat":
                await websocket.send_json({"type": "heartbeat"})
            elif data.get("type") == "message":
                request_id = data.get("id")
                payload = data.get("payload", {})

                try:
                    result = "test"  # Placeholder for conversion logic
                    await websocket.send_json(
                        {
                            "type": "message",
                            "id": request_id,
                            "payload": result,
                        }
                    )
                except Exception as e:
                    error_message = str(e)
                    await websocket.send_json(
                        {
                            "type": "error",
                            "id": request_id,
                            "message": f"Unable to convert stake. Error: {error_message}",
                        }
                    )
    except asyncio.TimeoutError:
        await websocket.close(code=1001, reason="No heartbeat received.")
    except WebSocketDisconnect:
        logger.info("Client disconnected")

import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from exchange_rate.logging.logger import AppLogger

# Get the custom logger instance
logger = AppLogger.get_instance().get_logger()


class AppMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Log the start of request processing
        start_time = time.time()
        logger.info("Received %s request for %s", request.method, request.url)

        # Process the request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        # Log the end of request processing with additional data
        logger.info(
            "Completed %s request for %s with status code %s in %.4f seconds",
            request.method,
            request.url,
            response.status_code,
            process_time,
        )

        return response

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, RedirectResponse

from exchange_rate.api.dependencies.core_dependencies import app_lifespan
from exchange_rate.api.endpoints.conversion_route import (
    websocket_router as conversion_route,
)
from exchange_rate.api.middleware.middleware import AppMiddleware
from exchange_rate.config import APP_NAME, config

app = FastAPI(
    title=APP_NAME,
    version="0.1.0",
    default_response_class=ORJSONResponse,
    redirect_slashes=False,
    lifespan=app_lifespan,
    debug=config.ENVIRONMENT == "local",
)

app.add_middleware(AppMiddleware)

app.include_router(conversion_route, prefix="/conversion_route")


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url="/docs")

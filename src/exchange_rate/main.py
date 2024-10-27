from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from exchange_rate.api.dependencies.core_dependencies import app_lifespan
from exchange_rate.api.middleware.middleware import AppMiddleware
from exchange_rate.config import APP_NAME, config

app = FastAPI(
    title=APP_NAME,
    version="0.1.0",
    default_response_class=ORJSONResponse,
    lifespan=app_lifespan,
    debug=config.ENVIRONMENT == "local",
)

app.add_middleware(AppMiddleware)

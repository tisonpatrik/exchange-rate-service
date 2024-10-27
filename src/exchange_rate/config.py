from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_NAME = "exchange_rate_service"

HEARTBEAT_INTERVAL = 1  # Interval for sending heartbeats (in seconds)
HEARTBEAT_TIMEOUT = 2  # Time after which connection should be refreshed

BASE_CURRENCY = "EUR"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    ENVIRONMENT: Literal["local", "test", "prod"]

    # Redis
    REDIS_URL: str
    MAX_REDIS_CONNECTIONS: int
    REDIS_SOCKET_TIMEOUT: int
    REDIS_SOCKET_CONNECT_TIMEOUT: int

    CURRENCY_ASSIGNMENT_URL: str

    FREECURRENCYAPI_KEY: str


config = Settings()  # type: ignore

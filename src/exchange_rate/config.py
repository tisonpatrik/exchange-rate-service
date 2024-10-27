from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_NAME = "exchange_rate_service"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    ENVIRONMENT: Literal["local", "test", "prod"]

    # Redis
    REDIS_URL: str
    MAX_REDIS_CONNECTIONS: int
    REDIS_SOCKET_TIMEOUT: int
    REDIS_SOCKET_CONNECT_TIMEOUT: int


config = Settings()  # type: ignore

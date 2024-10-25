from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_NAME = "gallery_service"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    ENVIRONMENT: Literal["local", "test", "prod"]

    # Redis
    REDIS: str


config = Settings()  # type: ignore

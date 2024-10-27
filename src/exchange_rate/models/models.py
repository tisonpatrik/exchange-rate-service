from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class HeartbeatMessage(BaseModel):
    type: str = Field(default="heartbeat")


class ConversionRequestPayload(BaseModel):
    marketId: int
    selectionId: int
    odds: float
    stake: Decimal = Field(max_digits=10, decimal_places=5)
    currency: str
    date: datetime


class ConversionRequestMessage(BaseModel):
    type: str = Field(default="message")
    id: int
    payload: ConversionRequestPayload


class ConversionResponsePayload(ConversionRequestPayload):
    stake: Decimal = Field(max_digits=10, decimal_places=5)
    currency: str
    date: datetime


class ConversionResponseMessage(BaseModel):
    type: str = Field(default="message")
    id: int
    payload: ConversionResponsePayload


class ConversionErrorMessage(BaseModel):
    type: str = Field(default="error")
    id: int
    message: str

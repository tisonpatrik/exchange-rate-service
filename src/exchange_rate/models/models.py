from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class HeartbeatMessage(BaseModel):
    type: Literal["heartbeat"]


class ConversionRequestPayload(BaseModel):
    marketId: int
    selectionId: int
    odds: float
    stake: Decimal = Field(max_digits=10, decimal_places=5)
    currency: str
    date: datetime


class ConversionRequestMessage(BaseModel):
    type: Literal["message"]
    id: int
    payload: ConversionRequestPayload


class ConversionResponsePayload(ConversionRequestPayload):
    stake: Decimal = Field(max_digits=10, decimal_places=5)
    currency: Literal["EUR"]
    date: datetime


class ConversionResponseMessage(BaseModel):
    type: Literal["message"]
    id: int
    payload: ConversionResponsePayload


class ConversionErrorMessage(BaseModel):
    type: Literal["error"]
    id: int
    message: str

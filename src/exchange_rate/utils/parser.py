from typing import Tuple, Union

from pydantic import ValidationError

from exchange_rate.models.models import (
    ConversionErrorMessage,
    ConversionRequestMessage,
    HeartbeatMessage,
)


def parse(
    raw_data: dict,
) -> Tuple[
    Union[HeartbeatMessage, ConversionRequestMessage, ConversionErrorMessage], bool
]:
    message_type = raw_data.get("type")

    try:
        if message_type == "heartbeat":
            return HeartbeatMessage(**raw_data), True
        elif message_type == "message":
            return ConversionRequestMessage(**raw_data), True
        else:
            return ConversionErrorMessage(
                type="error",
                id=raw_data.get("id", 0),
                message="Unsupported message type",
            ), False
    except ValidationError:
        return ConversionErrorMessage(
            type="error", id=raw_data.get("id", 0), message="Invalid message payload"
        ), False

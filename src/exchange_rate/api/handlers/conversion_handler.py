from exchange_rate.models.models import (
    ConversionRequestPayload,
)
from exchange_rate.services.convertion_service import ConversionService


class ConversionHandler:
    def __init__(self):
        self.exchange_service = ConversionService()

    async def handle_conversion_request(self, data: ConversionRequestPayload):
        """
        Handles the conversion request and returns a structured response message.
        """
        try:
            pass

        except Exception:
            pass

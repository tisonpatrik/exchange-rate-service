from datetime import datetime

from exchange_rate.models.models import (
    ConversionErrorMessage,
    ConversionRequestPayload,
    ConversionResponseMessage,
    ConversionResponsePayload,
)
from exchange_rate.services.convertion_service import ConversionService


class ConversionHandler:
    def __init__(self):
        self.exchange_service = ConversionService()

    async def handle_conversion_request(
        self, data: ConversionRequestPayload
    ) -> ConversionResponseMessage | ConversionErrorMessage:
        """
        Handles the conversion request and returns a structured response message.
        """
        request_id = data.id

        try:
            # Simulate exchange rate conversion logic
            converted_stake = round(
                data.payload.stake * 0.82, 5
            )  # Placeholder for conversion logic to EUR
            converted_date = datetime.utcnow()

            converted_data = ConversionResponsePayload(
                marketId=data.payload.marketId,
                selectionId=data.payload.selectionId,
                odds=data.payload.odds,
                stake=converted_stake,
                currency="EUR",
                date=converted_date,
            )

            return ConversionResponseMessage(
                type="message", id=request_id, payload=converted_data
            )

        except Exception as e:
            error_message = str(e)
            return ConversionErrorMessage(
                type="error",
                id=request_id,
                message=f"Unable to convert stake. Error: {error_message}",
            )

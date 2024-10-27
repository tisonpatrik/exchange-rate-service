from exchange_rate.config import BASE_CURRENCY
from exchange_rate.freecurrency.freecurrency_client import FreeCurrencyAPIClient
from exchange_rate.logging.logger import AppLogger
from exchange_rate.models.models import (
    ConversionErrorMessage,
    ConversionRequestMessage,
    ConversionResponseMessage,
    ConversionResponsePayload,
)
from exchange_rate.services.convertion_service import ConversionService


class ConversionHandler:
    def __init__(self, freecurrency_client: FreeCurrencyAPIClient):
        self.logger = AppLogger.get_instance().get_logger()
        self.freecurrency_client = freecurrency_client
        self.exchange_service = ConversionService()

    async def convert_to_base_currency_async(self, request: ConversionRequestMessage):
        try:
            self.logger.info("Converting stake to EUR: %s", request.json())
            exchange_rates = await self.freecurrency_client.get_latest_exchange_rates(base_currency=BASE_CURRENCY)

            if request.payload.currency not in exchange_rates.data:
                error_message = f"Unable to convert stake. Error: Currency '{request.payload.currency}' not available in exchange rates"
                return ConversionErrorMessage(id=request.id, message=error_message)

            # Perform conversion
            converted_stake = self.exchange_service.convert_currency(
                request.payload.stake,
                exchange_rates.data,
                target_currency=request.payload.currency,
            )

            # Prepare successful response payload
            response_payload = ConversionResponsePayload(
                marketId=request.payload.marketId,
                selectionId=request.payload.selectionId,
                odds=request.payload.odds,
                stake=converted_stake,
                currency=BASE_CURRENCY,
                date=request.payload.date,
            )

            response = ConversionResponseMessage(
                id=request.id,
                payload=response_payload,
            )
            self.logger.info("Successfully converted stake to %s: %s", BASE_CURRENCY, response.json())
            return response

        except Exception as e:
            # Handle unexpected errors with a generic error response
            error_response = ConversionErrorMessage(id=request.id, message=f"Unable to convert stake. Error: {e!s}")
            self.logger.exception("Conversion failed: %s", error_response.json())
            return error_response

from exchange_rate.config import BASE_CURRENCY
from exchange_rate.freecurrency.freecurrency_client import FreeCurrencyAPIClient
from exchange_rate.logging.logger import AppLogger
from exchange_rate.models.errors import ConversionServiceError
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
            exchange_rates = await self.freecurrency_client.get_latest_exchange_rates(base_currency=BASE_CURRENCY)
            converted_stake = self.exchange_service.convert_currency(
                request.payload.stake,
                exchange_rates.data,
                target_currency=request.payload.currency,
            )

            response_payload = ConversionResponsePayload(
                marketId=request.payload.marketId,
                selectionId=request.payload.selectionId,
                odds=request.payload.odds,
                stake=converted_stake,
                currency=BASE_CURRENCY,
                date=request.payload.date,
            )

            return ConversionResponseMessage(
                id=request.id,
                payload=response_payload,
            )

        except ConversionServiceError as e:
            # Only ConversionService errors are sent as a ConversionErrorMessage
            return ConversionErrorMessage(id=request.id, message=f"Unable to convert stake. Error: {e}")

        except Exception:
            # Other exceptions propagate as normal
            self.logger.exception("An unexpected error occurred in conversion.")
            raise

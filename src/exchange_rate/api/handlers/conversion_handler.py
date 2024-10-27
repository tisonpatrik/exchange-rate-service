from exchange_rate.config import BASE_CURRENCY
from exchange_rate.freecurrency.freecurrency_client import FreeCurrencyAPIClient
from exchange_rate.logging.logger import AppLogger
from exchange_rate.models.models import (
    ConversionErrorMessage,
    ConversionRequestMessage,
    ConversionResponseMessage,
    ConversionResponsePayload,
)
from exchange_rate.redis.redis_client import RedisClient
from exchange_rate.services.convertion_service import ConversionService


class ConversionHandler:
    def __init__(
        self, redis_client: RedisClient, freecurrency_client: FreeCurrencyAPIClient
    ):
        self.logger = AppLogger.get_instance().get_logger()
        self.redis_client = redis_client
        self.freecurrency_client = freecurrency_client
        self.exchange_service = ConversionService()

    async def convert_to_euros_async(self, request: ConversionRequestMessage):
        try:
            self.logger.info("Converting stake to EUR: %s", request.json())
            exchange_rate = self.freecurrency_client.get_latest_exchange_rate(
                base_currency=BASE_CURRENCY, target_currency=request.payload.currency
            )

            converted_stake = self.exchange_service.convert_to_eur(
                request.payload.stake, exchange_rate
            )

            response_payload = ConversionResponsePayload(
                marketId=request.payload.marketId,
                selectionId=request.payload.selectionId,
                odds=request.payload.odds,
                stake=converted_stake,
                currency="EUR",
                date=request.payload.date,
            )

            response = ConversionResponseMessage(
                id=request.id,
                payload=response_payload,
            )
            self.logger.info("Successfully converted stake to EUR: %s", response.json())
            return response
        except Exception as e:
            error_response = ConversionErrorMessage(
                id=request.id, message=f"Unable to convert stake. Error: {str(e)}"
            )
            self.logger.error("Conversion failed: %s", error_response.json())
            return error_response

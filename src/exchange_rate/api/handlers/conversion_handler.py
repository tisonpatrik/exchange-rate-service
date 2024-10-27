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
    def __init__(self, redis_client: RedisClient):
        self.logger = AppLogger.get_instance().get_logger()
        self.redis_client = redis_client
        self.exchange_service = ConversionService()

    async def convert_to_euros_async(self, request: ConversionRequestMessage):
        try:
            exchange_rate = await self.exchange_service.get_exchange_rate(
                request.payload.currency
            )

            converted_stake = round(request.payload.stake * exchange_rate, 5)

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

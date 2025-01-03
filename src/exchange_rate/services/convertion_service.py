from decimal import ROUND_DOWN, Decimal

from exchange_rate.logging.logger import AppLogger
from exchange_rate.models.errors import ConversionServiceError


class ConversionService:
    def __init__(self):
        self.logger = AppLogger.get_instance().get_logger()

    def convert_currency(self, stake: Decimal, exchange_rates: dict[str, Decimal], target_currency: str) -> Decimal:
        try:
            converted_stake = stake / exchange_rates[target_currency]
            return converted_stake.quantize(Decimal("0.00001"), rounding=ROUND_DOWN)
        except KeyError:
            self.logger.warning("Conversion failed: Currency '%s' not found in exchange rates.", target_currency)
            raise ConversionServiceError(f"Currency '{target_currency}' not available in exchange rates.") from None
        except ZeroDivisionError:
            self.logger.warning("Conversion failed: Exchange rate for currency '%s' is zero.", target_currency)
            raise ConversionServiceError(f"Exchange rate for currency '{target_currency}' is zero.") from None

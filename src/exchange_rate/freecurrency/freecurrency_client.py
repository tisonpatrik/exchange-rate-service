from decimal import Decimal

from freecurrencyapi import Client

from exchange_rate.logging.logger import AppLogger


class FreeCurrencyAPIClient:
    def __init__(self, client: Client):
        self.client = client
        self.logger = AppLogger.get_instance().get_logger()

    def get_latest_exchange_rate(
        self, base_currency: str, target_currency: str
    ) -> Decimal:
        try:
            self.logger.info(
                "Retrieving exchange rate for %s to %s", base_currency, target_currency
            )
            result = self.client.latest(
                base_currency=base_currency, currencies=[target_currency]
            )
            exchange_rate = result["data"].get(target_currency)
            if exchange_rate is None:
                self.logger.error(
                    "Target currency '%s' not found in response.", target_currency
                )
                raise ValueError(f"Exchange rate for {target_currency} not available.")
            self.logger.info(
                "Retrieved exchange rate for %s to %s: %f",
                base_currency,
                target_currency,
                exchange_rate,
            )
            return Decimal(str(exchange_rate))
        except Exception as e:
            self.logger.exception(
                "Failed to retrieve exchange rate from %s to %s",
                base_currency,
                target_currency,
            )
            raise e

from decimal import Decimal

from exchange_rate.redis.base_statements.get_cache_statement import GetCacheStatement
from exchange_rate.redis.base_statements.set_cache_statement import SetCacheStatement
from exchange_rate.utils.cache_utils import convert_decimal_to_float, get_series_key

NAME = "exchange_rates"


class GetExchangeRatesCache(GetCacheStatement):
    def __init__(self, base_currency: str):
        super().__init__(parameter=base_currency)
        self.name = NAME

    @property
    def cache_key(self) -> str:
        return get_series_key(self.name, self.parameter)


class SetExchangeRatesCache(SetCacheStatement):
    def __init__(self, data: dict[str, Decimal], currency: str):
        super().__init__(data)
        self.currency = currency
        self.name = NAME

    @property
    def cache_key(self) -> str:
        return get_series_key(self.name, self.currency)

    @property
    def cache_value(self) -> dict:
        return convert_decimal_to_float(self.values)

from decimal import Decimal


class ConversionService:
    def convert_to_eur(self, stake: Decimal, exchange_rate: Decimal) -> Decimal:
        return stake / exchange_rate

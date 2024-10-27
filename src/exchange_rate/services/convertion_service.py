from decimal import ROUND_DOWN, Decimal


class ConversionService:
    @classmethod
    def convert_currency(cls, stake: Decimal, exchange_rates: dict[str, Decimal], target_currency: str) -> Decimal:
        if target_currency not in exchange_rates:
            raise KeyError(f"Currency '{target_currency}' not available in exchange rates.")

        converted_stake = stake / exchange_rates[target_currency]
        return converted_stake.quantize(Decimal("0.00001"), rounding=ROUND_DOWN)

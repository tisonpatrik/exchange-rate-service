from decimal import Decimal


def get_series_key(name: str, base_currency: str) -> str:
    parts = ["series", name, "of", base_currency]
    return ":".join(parts)


def convert_decimal_to_float(data: dict[str, Decimal]) -> dict[str, float]:
    """Converts all Decimal values in a dictionary to float for JSON serialization."""
    try:
        return {key: float(value) if isinstance(value, Decimal) else value for key, value in data.items()}
    except Exception as e:
        raise ValueError(f"Error converting Decimal values to float: {e!s}") from e

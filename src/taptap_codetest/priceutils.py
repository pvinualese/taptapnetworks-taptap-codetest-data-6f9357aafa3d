"""Parsing of the event `price_micros` field, shared by cleaning and transformation."""

from __future__ import annotations

import math
from typing import Any


class PriceParseError(ValueError):
    pass


def parse_price_micros(value: Any) -> float:
    """Return `value` as a finite float.

    Accepted: int, float, or a string holding a number, including
    scientific notation (e.g. `"1.2e3"`). Booleans, `None`, non-numeric
    strings, and non-finite values (`nan`/`inf`) are all rejected.
    """
    if isinstance(value, bool):
        raise PriceParseError(f"unsupported price_micros type: {value!r}")
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        try:
            number = float(value)
        except ValueError as exc:
            raise PriceParseError(f"invalid price_micros value: {value!r}") from exc
    else:
        raise PriceParseError(f"unsupported price_micros type: {value!r}")

    if not math.isfinite(number):
        raise PriceParseError(f"invalid price_micros value: {value!r}")
    return number

from __future__ import annotations

from taptap_codetest.cleaning.base import CleaningRule
from taptap_codetest.priceutils import PriceParseError, parse_price_micros
from taptap_codetest.records import Record


class ValidImpressionPriceRule(CleaningRule):
    """Drops impressions whose `price_micros` can't be parsed or isn't
    strictly positive. Ignored on every other event type — bid requests
    and clicks don't carry a meaningful price.
    """

    def check(self, record: Record) -> str | None:
        if record.payload.get("event_type") != "impression":
            return None

        price = record.payload.get("price_micros")
        try:
            value = parse_price_micros(price)
        except PriceParseError as exc:
            return f"invalid_price: {exc}"
        if value <= 0:
            return f"invalid_price: price_micros must be > 0, got {price!r}"
        return None

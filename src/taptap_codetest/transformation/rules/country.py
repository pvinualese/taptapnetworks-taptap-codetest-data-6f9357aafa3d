from __future__ import annotations

from typing import Any

from taptap_codetest.records import Record
from taptap_codetest.transformation.base import TransformationRule

VALID_MARKETS = {"ES", "FR", "IT", "PT", "DE", "GB"}
UNKNOWN_MARKET = "XX"

# The feed also sends these markets as their ISO 3166-1 alpha-3 code.
_ALPHA3_TO_ALPHA2 = {
    "ESP": "ES",
    "FRA": "FR",
    "ITA": "IT",
    "PRT": "PT",
    "DEU": "DE",
    "GBR": "GB",
}


class NormalizeCountryRule(TransformationRule):
    """Normalizes `country` to one of ES, FR, IT, PT, DE, GB, or `XX`.

    Handles lower/mixed case (`"es"` -> `"ES"`), surrounding whitespace,
    and the three-letter variant the feed sends for the same six markets
    (`"ESP"` -> `"ES"`, `"deu"` -> `"DE"`, ...). Anything else — an
    unrelated code, garbage, or a missing value — becomes `XX`; the
    country is never dropped, only relabelled.
    """

    def apply(self, record: Record) -> Record:
        normalized = self._normalize(record.payload.get("country"))
        return record.with_payload({**record.payload, "country": normalized})

    def _normalize(self, raw: Any) -> str:
        if not isinstance(raw, str):
            return UNKNOWN_MARKET
        code = raw.strip().upper()
        code = _ALPHA3_TO_ALPHA2.get(code, code)
        return code if code in VALID_MARKETS else UNKNOWN_MARKET

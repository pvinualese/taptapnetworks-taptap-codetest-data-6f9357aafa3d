import pandas as pd
import pytest

from taptap_codetest.records import Record
from taptap_codetest.transformation.rules.country import NormalizeCountryRule
from taptap_codetest.transformation.rules.publisher import EnrichPublisherNameRule


def _country_record(country):
    return Record(payload={"country": country})


@pytest.mark.parametrize(
    "value",
    ["ES", "FR", "IT", "PT", "DE", "GB"],
)
def test_already_valid_codes_are_left_untouched(value):
    rule = NormalizeCountryRule()
    result = rule.apply(_country_record(value))
    assert result.payload["country"] == value


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("es", "ES"),
        ("fr", "FR"),
        ("it", "IT"),
        ("pt", "PT"),
        ("de", "DE"),
        ("gb", "GB"),
    ],
)
def test_lowercase_is_uppercased(value, expected):
    rule = NormalizeCountryRule()
    result = rule.apply(_country_record(value))
    assert result.payload["country"] == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("ESP", "ES"),
        ("FRA", "FR"),
        ("ITA", "IT"),
        ("PRT", "PT"),
        ("DEU", "DE"),
        ("GBR", "GB"),
    ],
)
def test_alpha3_variants_are_mapped_to_alpha2(value, expected):
    rule = NormalizeCountryRule()
    result = rule.apply(_country_record(value))
    assert result.payload["country"] == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("esp", "ES"),
        ("deu", "DE"),
        ("gbr", "GB"),
    ],
)
def test_lowercase_alpha3_variants_are_mapped_and_uppercased(value, expected):
    rule = NormalizeCountryRule()
    result = rule.apply(_country_record(value))
    assert result.payload["country"] == expected


@pytest.mark.parametrize("value", [" DE ", " es ", "\tFR\n"])
def test_surrounding_whitespace_is_stripped(value):
    rule = NormalizeCountryRule()
    result = rule.apply(_country_record(value))
    assert result.payload["country"] in {"DE", "ES", "FR"}


@pytest.mark.parametrize("value", ["", "??", "ZZ", "unknown", "US", None])
def test_unrecognized_or_missing_values_become_xx(value):
    rule = NormalizeCountryRule()
    result = rule.apply(_country_record(value))
    assert result.payload["country"] == "XX"


def test_other_payload_fields_are_preserved():
    rule = NormalizeCountryRule()
    record = Record(payload={"country": "esp", "event_id": "br_1"})
    result = rule.apply(record)
    assert result.payload["event_id"] == "br_1"
    assert result.payload["country"] == "ES"


def _publishers():
    return pd.DataFrame(
        {
            "publisher_id": ["pub_001", "pub_002"],
            "publisher_name": ["El Diario Digital", "RadioVoz"],
        }
    )


def test_known_publisher_id_resolves_its_name():
    rule = EnrichPublisherNameRule(_publishers())
    record = Record(payload={"publisher_id": "pub_002"})
    result = rule.apply(record)
    assert result.payload["publisher_name"] == "RadioVoz"


def test_unknown_publisher_id_becomes_unknown():
    rule = EnrichPublisherNameRule(_publishers())
    record = Record(payload={"publisher_id": "pub_999"})
    result = rule.apply(record)
    assert result.payload["publisher_name"] == "UNKNOWN"


def test_missing_publisher_id_becomes_unknown():
    rule = EnrichPublisherNameRule(_publishers())
    record = Record(payload={})
    result = rule.apply(record)
    assert result.payload["publisher_name"] == "UNKNOWN"


def test_publisher_lookup_preserves_other_payload_fields():
    rule = EnrichPublisherNameRule(_publishers())
    record = Record(payload={"publisher_id": "pub_001", "event_id": "br_1"})
    result = rule.apply(record)
    assert result.payload["event_id"] == "br_1"
    assert result.payload["publisher_name"] == "El Diario Digital"

import pytest

from taptap_codetest.priceutils import PriceParseError, parse_price_micros


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (250000, 250000.0),
        (250000.5, 250000.5),
        ("250000", 250000.0),
        ("1.2e3", 1200.0),
        ("-1.2e3", -1200.0),
        ("0", 0.0),
    ],
)
def test_accepted_values(value, expected):
    assert parse_price_micros(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "abc",
        "12a",
        True,
        False,
        [250000],
        {"amount": 250000},
        float("nan"),
        float("inf"),
        "nan",
        "inf",
    ],
)
def test_rejected_values(value):
    with pytest.raises(PriceParseError):
        parse_price_micros(value)

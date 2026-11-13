"""Concrete `TransformationRule` implementations, applied in `default_rules()` order."""

import pandas as pd

from taptap_codetest.transformation.base import TransformationRule
from taptap_codetest.transformation.rules.country import NormalizeCountryRule
from taptap_codetest.transformation.rules.publisher import EnrichPublisherNameRule
from taptap_codetest.transformation.rules.timestamp import DeriveUtcDateHourRule


def default_rules(publishers: pd.DataFrame) -> list[TransformationRule]:
    """`EnrichPublisherNameRule` needs the publisher dimension, which is
    only known once `--input` is resolved, so this is a factory rather
    than a module-level constant.
    """
    return [
        DeriveUtcDateHourRule(),
        NormalizeCountryRule(),
        EnrichPublisherNameRule(publishers),
    ]

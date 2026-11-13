"""Concrete `TransformationRule` implementations, applied in `DEFAULT_RULES` order."""

from taptap_codetest.transformation.base import TransformationRule
from taptap_codetest.transformation.rules.timestamp import DeriveUtcDateHourRule

DEFAULT_RULES: list[TransformationRule] = [
    DeriveUtcDateHourRule(),
]

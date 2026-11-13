"""Concrete `CleaningRule` implementations, applied in `default_rules()` order."""

from taptap_codetest.cleaning.base import CleaningRule
from taptap_codetest.cleaning.rules.duplicate import DuplicateLineRule
from taptap_codetest.cleaning.rules.price import ValidImpressionPriceRule
from taptap_codetest.cleaning.rules.timestamp import ValidTimestampRule


def default_rules() -> list[CleaningRule]:
    """Fresh rule instances for one pipeline run.

    `DuplicateLineRule` carries per-run state (the lines it has seen), so
    it can't be shared, module-level, across runs the way a stateless rule
    could — each call here returns its own instance.
    """
    return [
        DuplicateLineRule(),
        ValidTimestampRule(),
        ValidImpressionPriceRule(),
    ]

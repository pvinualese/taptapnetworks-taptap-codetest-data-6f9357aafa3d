from taptap_codetest.cleaning.rules.duplicate import DuplicateLineRule
from taptap_codetest.cleaning.rules.price import ValidImpressionPriceRule
from taptap_codetest.cleaning.rules.timestamp import ValidTimestampRule
from taptap_codetest.records import Record


def _record(raw_line, source_file="events.jsonl", line_number=1):
    return Record(payload={}, source_file=source_file, line_number=line_number, raw_line=raw_line)


def test_first_occurrence_is_kept():
    rule = DuplicateLineRule()
    assert rule.check(_record('{"event_id": "a"}', line_number=1)) is None


def test_later_identical_line_is_rejected_as_duplicate():
    rule = DuplicateLineRule()
    line = '{"event_id": "a"}'
    assert rule.check(_record(line, line_number=1)) is None
    reason = rule.check(_record(line, line_number=5))
    assert reason == "duplicate_line: duplicate of events.jsonl:1"


def test_duplicate_across_files_is_still_caught():
    rule = DuplicateLineRule()
    line = '{"event_id": "a"}'
    assert rule.check(_record(line, source_file="day1.jsonl", line_number=3)) is None
    reason = rule.check(_record(line, source_file="day2.jsonl", line_number=7))
    assert reason == "duplicate_line: duplicate of day1.jsonl:3"


def test_non_identical_lines_are_not_duplicates():
    rule = DuplicateLineRule()
    assert rule.check(_record('{"event_id": "a"}')) is None
    assert rule.check(_record('{"event_id": "b"}')) is None


def test_fresh_rule_instance_has_no_memory_of_previous_runs():
    line = '{"event_id": "a"}'
    first_run = DuplicateLineRule()
    first_run.check(_record(line))

    second_run = DuplicateLineRule()
    assert second_run.check(_record(line)) is None


def _event_record(event_type, price_micros):
    return Record(payload={"event_type": event_type, "price_micros": price_micros})


def test_impression_with_valid_price_is_kept():
    rule = ValidImpressionPriceRule()
    for price in (250000, 250000.5, "250000", "1.2e3"):
        assert rule.check(_event_record("impression", price)) is None


def test_impression_with_unparseable_price_is_rejected():
    rule = ValidImpressionPriceRule()
    reason = rule.check(_event_record("impression", "not-a-number"))
    assert reason.startswith("invalid_price:")


def test_impression_with_missing_price_is_rejected():
    rule = ValidImpressionPriceRule()
    reason = rule.check(_event_record("impression", None))
    assert reason.startswith("invalid_price:")


def test_impression_with_zero_or_negative_price_is_rejected():
    rule = ValidImpressionPriceRule()
    assert rule.check(_event_record("impression", 0)).startswith("invalid_price:")
    assert rule.check(_event_record("impression", -1)).startswith("invalid_price:")


def test_price_is_ignored_on_non_impression_events():
    rule = ValidImpressionPriceRule()
    assert rule.check(_event_record("bid_request", None)) is None
    assert rule.check(_event_record("bid_request", "garbage")) is None
    assert rule.check(_event_record("click", -1)) is None


def _ts_record(ts):
    return Record(payload={"ts": ts})


def test_timestamp_inside_plausible_window_is_kept():
    rule = ValidTimestampRule()
    assert rule.check(_ts_record("2026-08-25T00:00:00Z")) is None
    assert rule.check(_ts_record("2026-09-01T12:00:00Z")) is None
    assert rule.check(_ts_record("2026-09-09T23:59:59Z")) is None


def test_timestamp_before_window_start_is_rejected():
    rule = ValidTimestampRule()
    reason = rule.check(_ts_record("2026-08-24T23:59:59Z"))
    assert reason.startswith("implausible_ts:")


def test_timestamp_at_or_after_window_end_is_rejected():
    rule = ValidTimestampRule()
    assert rule.check(_ts_record("2026-09-10T00:00:00Z")).startswith("implausible_ts:")
    assert rule.check(_ts_record("2026-09-15T00:00:00Z")).startswith("implausible_ts:")


def test_timestamp_still_rejected_for_bad_format():
    rule = ValidTimestampRule()
    assert rule.check(_ts_record("not-a-timestamp")).startswith("invalid_ts:")

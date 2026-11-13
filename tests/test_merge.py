from taptap_codetest.cleaning.merge import EventIdMerger
from taptap_codetest.records import Record


def _record(payload, **provenance):
    return Record(payload=payload, **provenance)


def test_single_record_passes_through_unchanged():
    merger = EventIdMerger()
    record = _record({"event_id": "a", "country": "ES"})
    (result,) = list(merger.merge([record]))
    assert result is record
    assert merger.rejections == []


def test_stale_copy_is_rejected_and_the_most_recent_one_passes_through():
    merger = EventIdMerger()
    older = _record(
        {"event_id": "a", "ts": "2026-09-01T10:00:00Z", "country": "ES"},
        source_file="f.jsonl",
        line_number=1,
    )
    newer = _record(
        {"event_id": "a", "ts": "2026-09-01T10:05:00Z", "country": "FR"},
        source_file="f.jsonl",
        line_number=2,
    )
    (result,) = list(merger.merge([older, newer]))

    assert result.payload == newer.payload
    assert len(merger.rejections) == 1
    assert merger.rejections[0].line_number == 1
    assert merger.rejections[0].reason.startswith("stale_event_id:")


def test_stale_copy_is_rejected_regardless_of_arrival_order():
    merger = EventIdMerger()
    newer = _record({"event_id": "a", "ts": "2026-09-01T10:05:00Z", "country": "FR"})
    older = _record({"event_id": "a", "ts": "2026-09-01T10:00:00Z", "country": "ES"})
    (result,) = list(merger.merge([newer, older]))  # newer arrives first

    assert result.payload["country"] == "FR"
    assert len(merger.rejections) == 1


def test_ts_encodings_are_compared_by_instant_not_by_text():
    merger = EventIdMerger()
    # 1788256800000 is 2026-09-01T10:00:00Z in epoch millis — earlier than the ISO copy below.
    older = _record({"event_id": "a", "ts": 1788256800000, "country": "ES"})
    newer = _record({"event_id": "a", "ts": "2026-09-01T10:05:00Z", "country": "FR"})
    (result,) = list(merger.merge([older, newer]))

    assert result.payload["country"] == "FR"
    assert len(merger.rejections) == 1


def test_differing_fields_become_null_when_the_surviving_copies_share_the_same_ts():
    merger = EventIdMerger()
    a = _record({"event_id": "a", "ts": "2026-09-01T10:00:00Z", "price_micros": 100})
    b = _record({"event_id": "a", "ts": "2026-09-01T10:00:00Z", "price_micros": 200})
    (result,) = list(merger.merge([a, b]))

    assert result.payload["ts"] == "2026-09-01T10:00:00Z"  # agrees, kept
    assert result.payload["price_micros"] is None  # differs, no ts left to break the tie
    assert merger.rejections == []  # nothing was stale, both share the winning ts


def test_three_copies_reject_the_stale_one_then_null_the_remaining_disagreement():
    """The exact scenario reported: three copies of the same event_id, two
    share the most recent ts (but disagree on publisher_id/country), one
    has an older ts and must be rejected outright.
    """
    merger = EventIdMerger()
    a = _record(
        {
            "event_id": "br_008888",
            "event_type": "bid_request",
            "ts": "2026-09-02T02:31:51+02:00",
            "publisher_id": "pub_008",
            "country": "ESP",
            "device": "desktop",
        },
        source_file="events-test.jsonl",
        line_number=50,
    )
    b = _record(
        {
            "event_id": "br_008888",
            "event_type": "bid_request",
            "ts": "2026-09-02T02:31:51+02:00",
            "publisher_id": "pub_007",
            "country": "FRA",
            "device": "desktop",
        },
        source_file="events-test.jsonl",
        line_number=51,
    )
    stale = _record(
        {
            "event_id": "br_008888",
            "event_type": "bid_request",
            "ts": "2026-09-01T02:31:51+02:00",
            "publisher_id": "pub_tests",
            "country": "FRA",
            "device": "desktop",
        },
        source_file="events-test.jsonl",
        line_number=52,
    )

    (result,) = list(merger.merge([a, b, stale]))

    assert len(merger.rejections) == 1
    assert merger.rejections[0].line_number == 52
    assert merger.rejections[0].reason.startswith("stale_event_id:")

    assert result.payload["ts"] == "2026-09-02T02:31:51+02:00"  # agrees between a and b, kept
    assert result.payload["event_type"] == "bid_request"  # agrees, kept
    assert result.payload["device"] == "desktop"  # agrees, kept
    assert result.payload["publisher_id"] is None  # differs between a and b
    assert result.payload["country"] is None  # differs between a and b


def test_records_with_missing_event_id_are_never_merged_together():
    merger = EventIdMerger()
    a = _record({"event_id": None, "price_micros": 100})
    b = _record({"event_id": None, "price_micros": 200})
    results = list(merger.merge([a, b]))

    assert len(results) == 2
    assert {r.payload["price_micros"] for r in results} == {100, 200}
    assert merger.rejections == []


def test_unrelated_events_are_left_alone():
    merger = EventIdMerger()
    a = _record({"event_id": "a", "country": "ES"})
    b = _record({"event_id": "b", "country": "FR"})
    results = list(merger.merge([a, b]))

    assert [r.payload["event_id"] for r in results] == ["a", "b"]
    assert merger.rejections == []

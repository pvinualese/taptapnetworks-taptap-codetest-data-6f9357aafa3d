import json

import pandas as pd

from taptap_codetest.cli import build_pipeline


def _event(event_id, event_type, ts, price=None):
    return json.dumps(
        {
            "event_id": event_id,
            "event_type": event_type,
            "ts": ts,
            "publisher_id": "pub_001",
            "country": "ES",
            "price_micros": price,
        }
    )


def test_pipeline_aggregates_and_writes_rejections(tmp_path):
    input_dir = tmp_path / "in"
    output_dir = tmp_path / "out"
    input_dir.mkdir()
    (input_dir / "publishers.csv").write_text(
        "publisher_id,publisher_name,tier\npub_001,El Diario Digital,premium\n"
    )
    bad_ts_line = _event("br_3", "bid_request", "2026/09/01 10:00")
    bad_price_line = _event("im_3", "impression", 1788257700000, price=0)
    redelivered_line = _event("br_1", "bid_request", "2026-09-01T10:15:00Z")
    lines = [
        redelivered_line,
        _event("br_2", "bid_request", "2026-09-01 12:30:00"),  # Madrid -> 10h UTC
        _event("im_1", "impression", 1788257700000, price=250000),
        _event("im_2", "impression", "1788257700000", price=750000),
        bad_price_line,  # impression with a non-positive price is rejected outright
        _event("ck_1", "click", "2026-09-01T12:45:00+02:00"),
        bad_ts_line,
        '{"event_id": "br_4", event_type: "bid_request"}',
        redelivered_line,  # at-least-once redelivery of the first line, byte-identical
    ]
    (input_dir / "events.jsonl").write_text("\n".join(lines) + "\n")

    build_pipeline(input_dir).run(input_dir, output_dir)

    metrics = pd.read_csv(output_dir / "metrics.csv")
    assert metrics.to_dict("records") == [
        {
            "date_utc": "2026-09-01",
            "hour_utc": 10,
            "country": "ES",
            "publisher_id": "pub_001",
            "publisher_name": "El Diario Digital",
            "bid_requests": 2,
            "impressions": 2,
            "clicks": 1,
            "ctr": 0.5,
            "spend_eur": 1.0,
        }
    ]

    rejected = [
        json.loads(line)
        for line in (output_dir / "rejected.jsonl").read_text().splitlines()
    ]
    assert [(r["line_number"], r["reason"].split(":")[0]) for r in rejected] == [
        (5, "invalid_price"),
        (7, "invalid_ts"),
        (8, "invalid_json"),
        (9, "duplicate_line"),
    ]
    assert rejected[0]["raw_line"] == bad_price_line
    assert rejected[1]["raw_line"] == bad_ts_line
    assert rejected[1]["source_file"].endswith("events.jsonl")
    assert rejected[3]["raw_line"] == redelivered_line

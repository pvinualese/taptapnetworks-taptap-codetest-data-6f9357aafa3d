import json

import pandas as pd

from taptap_codetest.records import Rejection
from taptap_codetest.writing.csv_writer import CSVWriter
from taptap_codetest.writing.rejection_writer import RejectionWriter
from taptap_codetest.writing.summary_writer import SummaryWriter


def test_unpartitioned_table_is_written_flat(tmp_path):
    table = pd.DataFrame({"a": [1, 2]})
    CSVWriter().write({"events": table}, tmp_path)

    assert (tmp_path / "events.csv").exists()
    assert not (tmp_path / "a=1").exists()


def test_partitioned_table_is_split_into_one_folder_per_value(tmp_path):
    table = pd.DataFrame(
        {
            "date_utc": ["2026-09-01", "2026-09-01", "2026-09-02"],
            "value": [1, 2, 3],
        }
    )
    CSVWriter(partition_column="date_utc", partition_label="date").write(
        {"metrics": table}, tmp_path
    )

    day1 = pd.read_csv(tmp_path / "date=2026-09-01" / "metrics.csv")
    day2 = pd.read_csv(tmp_path / "date=2026-09-02" / "metrics.csv")
    assert day1["value"].tolist() == [1, 2]
    assert day2["value"].tolist() == [3]
    # the partition column stays in the file itself, only the folder is split on it
    assert list(day1.columns) == ["date_utc", "value"]


def test_table_without_the_partition_column_is_written_flat(tmp_path):
    table = pd.DataFrame({"value": [1, 2]})
    CSVWriter(partition_column="date_utc", partition_label="date").write(
        {"events": table}, tmp_path
    )

    assert (tmp_path / "events.csv").exists()


def test_rejection_writer_writes_under_its_own_subdirectory(tmp_path):
    rejections = [Rejection("invalid_ts: bad", "events.jsonl", 3, "{...}")]
    RejectionWriter().write(rejections, tmp_path)

    rejects_file = tmp_path / "_rejects" / "rejects.jsonl"
    assert rejects_file.exists()
    assert json.loads(rejects_file.read_text().splitlines()[0])["line_number"] == 3


def test_summary_writer_writes_the_given_counts(tmp_path):
    summary = {
        "lines_read": 10,
        "lines_accepted": 7,
        "lines_rejected": 3,
        "rejections_by_type": {"invalid_ts": 2, "duplicate_line": 1},
    }
    SummaryWriter().write(summary, tmp_path)

    summary_file = tmp_path / "_summary.json"
    assert summary_file.exists()
    assert json.loads(summary_file.read_text()) == summary

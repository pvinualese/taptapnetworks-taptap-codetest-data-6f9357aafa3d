"""Reference (dimension) data used to enrich events."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PUBLISHERS_FILENAME = "publishers.csv"


def load_publishers(input_path: Path) -> pd.DataFrame:
    input_dir = input_path.parent if input_path.is_file() else input_path
    csv_path = input_dir / PUBLISHERS_FILENAME
    if not csv_path.exists():
        return pd.DataFrame(columns=["publisher_id", "publisher_name"])
    return pd.read_csv(csv_path, usecols=["publisher_id", "publisher_name"])

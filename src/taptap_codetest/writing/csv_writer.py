from __future__ import annotations

from pathlib import Path

import pandas as pd

from taptap_codetest.writing.base import Writer


class CSVWriter(Writer):
    extension = ".csv"

    def _write_one(self, table: pd.DataFrame, path: Path) -> None:
        table.to_csv(path, index=False)

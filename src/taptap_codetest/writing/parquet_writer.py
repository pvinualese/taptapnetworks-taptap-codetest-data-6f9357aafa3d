from __future__ import annotations

from pathlib import Path

from taptap_codetest.tabular.base import TableSet
from taptap_codetest.writing.base import Writer


class ParquetWriter(Writer):
    def write(self, tables: TableSet, output_path: Path) -> None:
        output_path.mkdir(parents=True, exist_ok=True)
        for name, table in tables.items():
            table.to_parquet(output_path / f"{name}.parquet", index=False)

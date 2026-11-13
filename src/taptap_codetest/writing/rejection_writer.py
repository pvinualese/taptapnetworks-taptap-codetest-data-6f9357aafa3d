from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path

from taptap_codetest.records import Rejection


class RejectionWriter:
    """Writes one JSON object per discarded original line, under its own
    `dirname` subdirectory so it never collides with a date partition.
    """

    def __init__(self, dirname: str = "_rejects", filename: str = "rejects.jsonl") -> None:
        self.dirname = dirname
        self.filename = filename

    def write(self, rejections: Iterable[Rejection], output_path: Path) -> None:
        directory = output_path / self.dirname
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / self.filename).open("w", encoding="utf-8") as handle:
            for rejection in rejections:
                handle.write(json.dumps(asdict(rejection), ensure_ascii=False) + "\n")

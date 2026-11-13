from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path

from taptap_codetest.records import Rejection


class RejectionWriter:
    """Writes one JSON object per discarded original line."""

    def __init__(self, filename: str = "rejected.jsonl") -> None:
        self.filename = filename

    def write(self, rejections: Iterable[Rejection], output_path: Path) -> None:
        output_path.mkdir(parents=True, exist_ok=True)
        with (output_path / self.filename).open("w", encoding="utf-8") as handle:
            for rejection in rejections:
                handle.write(json.dumps(asdict(rejection), ensure_ascii=False) + "\n")

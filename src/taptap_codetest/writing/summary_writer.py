from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SummaryWriter:
    """Writes the run's summary counts as a single pretty-printed JSON file."""

    def __init__(self, filename: str = "_summary.json") -> None:
        self.filename = filename

    def write(self, summary: dict[str, Any], output_path: Path) -> None:
        output_path.mkdir(parents=True, exist_ok=True)
        with (output_path / self.filename).open("w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")

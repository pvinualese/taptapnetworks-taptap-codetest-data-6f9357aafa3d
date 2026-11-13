"""Default extractor: reads every `*.jsonl` file under a directory."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

from taptap_codetest.extraction.base import Extractor
from taptap_codetest.records import Record, Rejection


class JSONLExtractor(Extractor):
    """Reads one JSON object per line from `input_path` if it's a file, or
    from every `*.jsonl` file directly inside it if it's a directory (not
    recursive, so an output dir nested in the input dir isn't read back).

    Lines that aren't a valid JSON object are unparsable input rather than
    business-rule violations, so they're rejected here instead of being
    passed down to the cleaning layer.
    """

    def __init__(self, pattern: str = "*.jsonl") -> None:
        super().__init__()
        self.pattern = pattern

    def extract(self, input_path: Path) -> Iterator[Record]:
        if input_path.is_file():
            files = [input_path]
        else:
            files = sorted(input_path.glob(self.pattern))
        for file_path in files:
            yield from self._extract_file(file_path)

    def _extract_file(self, file_path: Path) -> Iterator[Record]:
        source = str(file_path)
        with file_path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                raw_line = line.rstrip("\r\n")
                if not raw_line.strip():
                    continue
                try:
                    payload = json.loads(raw_line)
                except json.JSONDecodeError as exc:
                    self.rejections.append(
                        Rejection(f"invalid_json: {exc.msg}", source, line_number, raw_line)
                    )
                    continue
                if not isinstance(payload, dict):
                    self.rejections.append(
                        Rejection("invalid_json: not an object", source, line_number, raw_line)
                    )
                    continue
                yield Record(payload, source, line_number, raw_line)

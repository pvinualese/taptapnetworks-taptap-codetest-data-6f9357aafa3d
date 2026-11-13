"""Wires the five layers together. Each is injected, so any layer can be
swapped (e.g. a different `Writer`) without touching the others.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from taptap_codetest.cleaning.base import Cleaner
from taptap_codetest.extraction.base import Extractor
from taptap_codetest.tabular.base import Tabulator
from taptap_codetest.transformation.base import Transformer
from taptap_codetest.writing.base import Writer
from taptap_codetest.writing.rejection_writer import RejectionWriter


@dataclass
class Pipeline:
    extractor: Extractor
    cleaner: Cleaner
    transformer: Transformer
    tabulator: Tabulator
    writer: Writer
    rejection_writer: RejectionWriter

    def run(self, input_path: Path, output_path: Path) -> None:
        records = self.extractor.extract(input_path)
        records = self.cleaner.clean(records)
        records = self.transformer.transform(records)
        # build() drains the lazy chain, so rejections are complete afterwards.
        tables = self.tabulator.build(records)
        self.writer.write(tables, output_path)

        rejections = sorted(
            [*self.extractor.rejections, *self.cleaner.rejections],
            key=lambda r: (r.source_file, r.line_number),
        )
        self.rejection_writer.write(rejections, output_path)

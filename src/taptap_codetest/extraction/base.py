"""Extraction layer: turns raw input files into `Record` objects.

This is the only layer that knows about file formats and I/O. Everything
downstream works on `Record` objects and has no knowledge of where they
came from.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path

from taptap_codetest.records import Record, Rejection


class Extractor(ABC):
    """Produces `Record` objects from a given input path.

    Lines that can't be turned into a `Record` are collected in `rejections`,
    which is complete once the `extract` iterator has been exhausted.
    """

    def __init__(self) -> None:
        self.rejections: list[Rejection] = []

    @abstractmethod
    def extract(self, input_path: Path) -> Iterator[Record]:
        """Yield one `Record` per readable event found under `input_path`."""

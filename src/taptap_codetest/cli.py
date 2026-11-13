"""`taptap-codetest --input <dir> --output <dir>` entry point."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from taptap_codetest.cleaning import Cleaner, EventIdMerger
from taptap_codetest.cleaning import default_rules as default_cleaning_rules
from taptap_codetest.extraction import JSONLExtractor
from taptap_codetest.pipeline import Pipeline
from taptap_codetest.reference import load_publishers
from taptap_codetest.tabular import MetricsTabulator
from taptap_codetest.transformation import Transformer
from taptap_codetest.transformation import default_rules as default_transformation_rules
from taptap_codetest.writing import WRITERS, RejectionWriter


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="taptap-codetest")
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="A .jsonl file, or a directory of *.jsonl files; publishers.csv is read from the same directory",
    )
    parser.add_argument(
        "--output", required=True, type=Path, help="Directory to write the resulting tables to"
    )
    parser.add_argument(
        "--format",
        choices=sorted(WRITERS),
        default="csv",
        help="Output table format (default: csv)",
    )
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)
    if not args.input.exists():
        parser.error(f"--input path does not exist: {args.input}")
    return args


def build_pipeline(input_path: Path, output_format: str = "csv") -> Pipeline:
    publishers = load_publishers(input_path)
    return Pipeline(
        extractor=JSONLExtractor(),
        cleaner=Cleaner(rules=default_cleaning_rules()),
        merger=EventIdMerger(),
        transformer=Transformer(rules=default_transformation_rules(publishers)),
        tabulator=MetricsTabulator(),
        writer=WRITERS[output_format](partition_column="date_utc", partition_label="date"),
        rejection_writer=RejectionWriter(),
    )


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=args.log_level)

    pipeline = build_pipeline(args.input, args.format)
    pipeline.run(args.input, args.output)

    logging.getLogger(__name__).info(
        "Rejected %d lines",
        len(pipeline.extractor.rejections)
        + len(pipeline.cleaner.rejections)
        + len(pipeline.merger.rejections),
    )


if __name__ == "__main__":
    main()

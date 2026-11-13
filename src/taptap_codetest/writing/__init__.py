from taptap_codetest.writing.base import Writer
from taptap_codetest.writing.csv_writer import CSVWriter
from taptap_codetest.writing.parquet_writer import ParquetWriter
from taptap_codetest.writing.rejection_writer import RejectionWriter
from taptap_codetest.writing.summary_writer import SummaryWriter

WRITERS: dict[str, type[Writer]] = {
    "csv": CSVWriter,
    "parquet": ParquetWriter,
}

__all__ = [
    "Writer",
    "CSVWriter",
    "ParquetWriter",
    "RejectionWriter",
    "SummaryWriter",
    "WRITERS",
]

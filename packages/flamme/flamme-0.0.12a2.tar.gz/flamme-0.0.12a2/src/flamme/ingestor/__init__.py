from __future__ import annotations

__all__ = [
    "BaseIngestor",
    "ClickHouseIngestor",
    "CsvIngestor",
    "Ingestor",
    "ParquetIngestor",
    "TransformedIngestor",
    "is_ingestor_config",
    "setup_ingestor",
]

from flamme.ingestor.base import BaseIngestor, is_ingestor_config, setup_ingestor
from flamme.ingestor.clickhouse import ClickHouseIngestor
from flamme.ingestor.csv import CsvIngestor
from flamme.ingestor.parquet import ParquetIngestor
from flamme.ingestor.transform import TransformedIngestor
from flamme.ingestor.vanilla import Ingestor

from __future__ import annotations

__all__ = ["CsvIngestor"]

import logging
from pathlib import Path

from pandas import DataFrame, read_csv

from flamme.ingestor.base import BaseIngestor
from flamme.utils.path import human_file_size, sanitize_path

logger = logging.getLogger(__name__)


class CsvIngestor(BaseIngestor):
    r"""Implements a CSV DataFrame ingestor.

    Args:
        path (``pathlib.Path`` or str): Specifies the path to the
            CSV file to ingest.
        **kwargs: Additional keyword arguments for
            ``pandas.read_csv``.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.ingestor import ParquetIngestor
        >>> ingestor = ParquetIngestor(path="/path/to/df.csv")
        >>> ingestor
        ParquetIngestor(path=/path/to/df.csv)
        >>> df = ingestor.ingest()  # doctest: +SKIP
    """

    def __init__(self, path: Path | str, **kwargs) -> None:
        self._path = sanitize_path(path)
        self._kwargs = kwargs

    def __repr__(self) -> str:
        args = ", ".join([f"{key}={value}" for key, value in self._kwargs.items()])
        if args:
            args = ", " + args
        return f"{self.__class__.__qualname__}(path={self._path}{args})"

    def ingest(self) -> DataFrame:
        logger.info(f"Ingesting CSV data from {self._path} (size={human_file_size(self._path)})...")
        df = read_csv(filepath_or_buffer=self._path, **self._kwargs)
        logger.info(f"Data ingested. DataFrame shape: {df.shape}")
        return df

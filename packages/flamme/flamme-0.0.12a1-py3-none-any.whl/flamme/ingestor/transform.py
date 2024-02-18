from __future__ import annotations

__all__ = ["TransformedIngestor"]

import logging

from coola.utils import str_indent, str_mapping
from pandas import DataFrame

from flamme.ingestor.base import BaseIngestor, setup_ingestor
from flamme.transformer.df.base import (
    BaseDataFrameTransformer,
    setup_dataframe_transformer,
)

logger = logging.getLogger(__name__)


class TransformedIngestor(BaseIngestor):
    r"""Implements an ingestor that also transforms the DataFrame.

    Args:
        path (``pathlib.Path`` or str): Specifies the path to the
            CSV file to ingest.
        transformer (``BaseDataFrameTransformer`` or dict): Specifies
            a ``pandas.DataFrame`` transformer or its configuration.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.ingestor import TransformedIngestor, ParquetIngestor
        >>> from flamme.transformer.df import ToNumeric
        >>> ingestor = TransformedIngestor(
        ...     ingestor=ParquetIngestor(path="/path/to/df.csv"),
        ...     transformer=ToNumeric(columns=["col1", "col3"]),
        ... )
        >>> ingestor
        TransformedIngestor(
          (ingestor): ParquetIngestor(path=/path/to/df.csv)
          (transformer): ToNumericDataFrameTransformer(columns=('col1', 'col3'))
        )
        >>> df = ingestor.ingest()  # doctest: +SKIP
    """

    def __init__(
        self, ingestor: BaseIngestor | dict, transformer: BaseDataFrameTransformer | dict
    ) -> None:
        self._ingestor = setup_ingestor(ingestor)
        self._transformer = setup_dataframe_transformer(transformer)

    def __repr__(self) -> str:
        args = str_indent(
            str_mapping({"ingestor": self._ingestor, "transformer": self._transformer})
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def ingest(self) -> DataFrame:
        df = self._ingestor.ingest()
        return self._transformer.transform(df)

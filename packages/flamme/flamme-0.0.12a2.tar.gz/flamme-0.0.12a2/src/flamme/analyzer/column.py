from __future__ import annotations

__all__ = ["ColumnSubsetAnalyzer"]

import logging
from collections.abc import Sequence

from coola.utils import str_indent, str_mapping
from pandas import DataFrame

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import BaseSection
from flamme.utils import setup_object

logger = logging.getLogger(__name__)


class ColumnSubsetAnalyzer(BaseAnalyzer):
    r"""Implements an analyzer to analyze only a subset of the columns.

    Args:
        columns (``Sequence``): Soecifies the columns to select.
        analyzer (``BaseAnalyzer`` or dict): Specifies the analyzer
            or its configuration.

    Example usage:

    .. code-block:: pycon

        >>> import numpy as np
        >>> import pandas as pd
        >>> from flamme.analyzer import ColumnSubsetAnalyzer, NullValueAnalyzer
        >>> analyzer = ColumnSubsetAnalyzer(columns=["int", "float"], analyzer=NullValueAnalyzer())
        >>> analyzer
        ColumnSubsetAnalyzer(
          (columns): 2 ['int', 'float']
          (analyzer): NullValueAnalyzer(figsize=None)
        )
        >>> df = pd.DataFrame(
        ...     {
        ...         "int": np.array([np.nan, 1, 0, 1]),
        ...         "float": np.array([1.2, 4.2, np.nan, 2.2]),
        ...         "str": np.array(["A", "B", None, np.nan]),
        ...     }
        ... )
        >>> section = analyzer.analyze(df)
    """

    def __init__(self, columns: Sequence[str], analyzer: BaseAnalyzer | dict) -> None:
        self._columns = list(columns)
        self._analyzer = setup_object(analyzer)

    def __repr__(self) -> str:
        args = str_indent(
            str_mapping(
                {"columns": f"{len(self._columns)} {self._columns}", "analyzer": self._analyzer}
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def analyze(self, df: DataFrame) -> BaseSection:
        logger.info(f"Selecting a {len(self._columns):,} columns: {self._columns}")
        df = df[self._columns]
        return self._analyzer.analyze(df)

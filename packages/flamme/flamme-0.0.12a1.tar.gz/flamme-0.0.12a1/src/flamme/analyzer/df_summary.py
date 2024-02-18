from __future__ import annotations

__all__ = ["DataFrameSummaryAnalyzer"]

import logging

from pandas import DataFrame

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import DataFrameSummarySection

logger = logging.getLogger(__name__)


class DataFrameSummaryAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer to show a short summary of the DataFrame.

    Args:
        top: Specifies the number of most frequent values to show.
        sort: If ``True``, sort the columns by alphabetical order.

    Example usage:

    ```pycon
    >>> import numpy as np
    >>> import pandas as pd
    >>> from flamme.analyzer import DataFrameSummaryAnalyzer
    >>> analyzer = DataFrameSummaryAnalyzer()
    >>> analyzer
    DataFrameSummaryAnalyzer(top=5, sort=False)
    >>> df = pd.DataFrame(
    ...     {
    ...         "col1": np.array([0, 1, 0, 1]),
    ...         "col2": np.array([1, 0, 1, 0]),
    ...         "col3": np.array([1, 1, 1, 1]),
    ...     }
    ... )
    >>> section = analyzer.analyze(df)

    ```
    """

    def __init__(self, top: int = 5, sort: bool = False) -> None:
        if top < 0:
            raise ValueError(f"Incorrect top value ({top}). top must be positive")
        self._top = top
        self._sort = bool(sort)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(top={self._top:,}, sort={self._sort})"

    def analyze(self, df: DataFrame) -> DataFrameSummarySection:
        logger.info("Analyzing the DataFrame...")
        if self._sort:
            df = df.reindex(sorted(df.columns), axis=1)
        return DataFrameSummarySection(df=df, top=self._top)

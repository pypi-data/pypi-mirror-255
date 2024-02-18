from __future__ import annotations

__all__ = ["DataTypeAnalyzer"]

import logging

from pandas import DataFrame

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import DataTypeSection
from flamme.utils.dtype import df_column_types

logger = logging.getLogger(__name__)


class DataTypeAnalyzer(BaseAnalyzer):
    r"""Implements an analyzer to find all the value types in each
    column.

    Example usage:

    .. code-block:: pycon

        >>> import numpy as np
        >>> import pandas as pd
        >>> from flamme.analyzer import DataTypeAnalyzer
        >>> analyzer = DataTypeAnalyzer()
        >>> analyzer
        DataTypeAnalyzer()
        >>> df = pd.DataFrame(
        ...     {
        ...         "int": np.array([np.nan, 1, 0, 1]),
        ...         "float": np.array([1.2, 4.2, np.nan, 2.2]),
        ...         "str": np.array(["A", "B", None, np.nan]),
        ...     }
        ... )
        >>> section = analyzer.analyze(df)
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def analyze(self, df: DataFrame) -> DataTypeSection:
        logger.info("Analyzing the data types...")
        return DataTypeSection(dtypes=df.dtypes.to_dict(), types=df_column_types(df))

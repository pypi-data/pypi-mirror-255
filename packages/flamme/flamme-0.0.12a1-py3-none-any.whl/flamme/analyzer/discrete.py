from __future__ import annotations

__all__ = ["ColumnDiscreteAnalyzer", "ColumnTemporalDiscreteAnalyzer"]

import logging
from collections import Counter

from pandas import DataFrame

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import (
    ColumnDiscreteSection,
    ColumnTemporalDiscreteSection,
    EmptySection,
)

logger = logging.getLogger(__name__)


class ColumnDiscreteAnalyzer(BaseAnalyzer):
    r"""Implements a discrete distribution analyzer.

    Args:
        column: Specifies the column to analyze.
        dropna: If ``True``, the NaN values are not included in the
            analysis.
        max_rows: Specifies the maximum number of rows to show in the
            table.
        yscale: Specifies the y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'`` scale is chosen based on the
            distribution.
        figsize: Specifies the figure size in inches. The first
            dimension is the width and the second is the height.

    Example usage:

    .. code-block:: pycon

        >>> import numpy as np
        >>> import pandas as pd
        >>> from flamme.analyzer import ColumnDiscreteAnalyzer
        >>> analyzer = ColumnDiscreteAnalyzer(column="str")
        >>> analyzer
        ColumnDiscreteAnalyzer(column=str, dropna=False, max_rows=20, yscale=auto, figsize=None)
        >>> df = pd.DataFrame(
        ...     {
        ...         "int": np.array([np.nan, 1, 0, 1]),
        ...         "float": np.array([1.2, 4.2, np.nan, 2.2]),
        ...         "str": np.array(["A", "B", None, np.nan]),
        ...     }
        ... )
        >>> section = analyzer.analyze(df)
    """

    def __init__(
        self,
        column: str,
        dropna: bool = False,
        max_rows: int = 20,
        yscale: str = "auto",
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._column = column
        self._dropna = bool(dropna)
        self._max_rows = max_rows
        self._yscale = yscale
        self._figsize = figsize

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(column={self._column}, "
            f"dropna={self._dropna}, max_rows={self._max_rows}, yscale={self._yscale}, "
            f"figsize={self._figsize})"
        )

    def analyze(self, df: DataFrame) -> ColumnDiscreteSection | EmptySection:
        logger.info(f"Analyzing the discrete distribution of {self._column}")
        if self._column not in df:
            logger.info(
                f"Skipping discrete distribution analysis of column {self._column} "
                f"because it is not in the DataFrame: {sorted(df.columns)}"
            )
            return EmptySection()
        return ColumnDiscreteSection(
            counter=Counter(df[self._column].value_counts(dropna=self._dropna).to_dict()),
            null_values=df[self._column].isnull().sum(),
            column=self._column,
            max_rows=self._max_rows,
            yscale=self._yscale,
            figsize=self._figsize,
        )


class ColumnTemporalDiscreteAnalyzer(BaseAnalyzer):
    r"""Implements an analyzer to show the temporal distribution of
    discrete values.

    Args:
        column (str): Specifies the column to analyze.
        dt_column (str): Specifies the datetime column used to analyze
            the temporal distribution.
        period (str): Specifies the temporal period e.g. monthly or
            daily.
        figsize (``tuple`` , optional): Specifies the figure size in
            inches. The first dimension is the width and the second is
            the height. Default: ``None``

    Example usage:

    .. code-block:: pycon

        >>> import numpy as np
        >>> import pandas as pd
        >>> from flamme.analyzer import ColumnTemporalDiscreteAnalyzer
        >>> analyzer = ColumnTemporalDiscreteAnalyzer(
        ...     column="str", dt_column="datetime", period="M"
        ... )
        >>> analyzer
        ColumnTemporalDiscreteAnalyzer(column=str, dt_column=datetime, period=M, figsize=None)
        >>> df = pd.DataFrame(
        ...     {
        ...         "int": np.array([np.nan, 1, 0, 1]),
        ...         "float": np.array([1.2, 4.2, np.nan, 2.2]),
        ...         "str": np.array(["A", "B", None, np.nan]),
        ...         "datetime": pd.to_datetime(
        ...             ["2020-01-03", "2020-02-03", "2020-03-03", "2020-04-03"]
        ...         ),
        ...     }
        ... )
        >>> section = analyzer.analyze(df)
    """

    def __init__(
        self,
        column: str,
        dt_column: str,
        period: str,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._column = column
        self._dt_column = dt_column
        self._period = period
        self._figsize = figsize

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(column={self._column}, "
            f"dt_column={self._dt_column}, period={self._period}, figsize={self._figsize})"
        )

    def analyze(self, df: DataFrame) -> ColumnTemporalDiscreteSection | EmptySection:
        logger.info(
            f"Analyzing the temporal discrete distribution of {self._column} | "
            f"datetime column: {self._dt_column} | period: {self._period}"
        )
        if self._column not in df:
            logger.info(
                "Skipping temporal discrete distribution analysis because the column "
                f"({self._column}) is not in the DataFrame: {sorted(df.columns)}"
            )
            return EmptySection()
        if self._dt_column not in df:
            logger.info(
                "Skipping temporal discrete distribution analysis because the datetime column "
                f"({self._dt_column}) is not in the DataFrame: {sorted(df.columns)}"
            )
            return EmptySection()
        return ColumnTemporalDiscreteSection(
            column=self._column,
            df=df,
            dt_column=self._dt_column,
            period=self._period,
            figsize=self._figsize,
        )

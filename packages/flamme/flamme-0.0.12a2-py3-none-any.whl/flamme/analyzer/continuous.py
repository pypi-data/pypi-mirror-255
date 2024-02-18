from __future__ import annotations

__all__ = ["ColumnContinuousAnalyzer", "ColumnTemporalContinuousAnalyzer"]

import logging

from pandas import DataFrame

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import (
    ColumnContinuousSection,
    ColumnTemporalContinuousSection,
    EmptySection,
)

logger = logging.getLogger(__name__)


class ColumnContinuousAnalyzer(BaseAnalyzer):
    r"""Implements an analyzer to show the temporal distribution of
    continuous values.

    Args:
        column: Specifies the column name.
        nbins: Specifies the number of bins in the histogram.
        yscale: Specifies the y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'/'symlog'`` scale is chosen based
            on the distribution.
        xmin: Specifies the minimum value of the range or its
            associated quantile. ``q0.1`` means the 10% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        xmax: Specifies the maximum value of the range or its
            associated quantile. ``q0.9`` means the 90% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        figsize: Specifies the figure size in inches. The first
            dimension is the width and the second is the height.

    Example usage:

    .. code-block:: pycon

        >>> import numpy as np
        >>> import pandas as pd
        >>> from flamme.analyzer import ColumnContinuousAnalyzer
        >>> analyzer = ColumnContinuousAnalyzer(column="float")
        >>> analyzer
        ColumnContinuousAnalyzer(column=float, nbins=None, yscale=auto, xmin=q0, xmax=q1, figsize=None)
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
        nbins: int | None = None,
        yscale: str = "auto",
        xmin: float | str | None = "q0",
        xmax: float | str | None = "q1",
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._column = column
        self._nbins = nbins
        self._yscale = yscale
        self._xmin = xmin
        self._xmax = xmax
        self._figsize = figsize

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(column={self._column}, nbins={self._nbins}, "
            f"yscale={self._yscale}, xmin={self._xmin}, xmax={self._xmax}, figsize={self._figsize})"
        )

    def analyze(self, df: DataFrame) -> ColumnContinuousSection | EmptySection:
        logger.info(f"Analyzing the continuous distribution of {self._column}")
        if self._column not in df:
            logger.info(
                "Skipping temporal continuous distribution analysis because the column "
                f"({self._column}) is not in the DataFrame: {sorted(df.columns)}"
            )
            return EmptySection()
        return ColumnContinuousSection(
            column=self._column,
            series=df[self._column],
            nbins=self._nbins,
            yscale=self._yscale,
            xmin=self._xmin,
            xmax=self._xmax,
            figsize=self._figsize,
        )


class ColumnTemporalContinuousAnalyzer(BaseAnalyzer):
    r"""Implements an analyzer to show the temporal distribution of
    continuous values.

    Args:
        column: Specifies the column to analyze.
        dt_column: Specifies the datetime column used to analyze
            the temporal distribution.
        period: Specifies the temporal period e.g. monthly or daily.
        yscale: Specifies the y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'/'symlog'`` scale is chosen based
            on the distribution.
        figsize: Specifies the figure size in inches. The first
            dimension is the width and the second is the height.

    Example usage:

    ```pycon
    >>> import numpy as np
    >>> import pandas as pd
    >>> from flamme.analyzer import TemporalNullValueAnalyzer
    >>> analyzer = ColumnTemporalContinuousAnalyzer(
    ...     column="float", dt_column="datetime", period="M"
    ... )
    >>> analyzer
    ColumnTemporalContinuousAnalyzer(column=float, dt_column=datetime, period=M, yscale=auto, figsize=None)
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

    ```
    """

    def __init__(
        self,
        column: str,
        dt_column: str,
        period: str,
        yscale: str = "auto",
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._column = column
        self._dt_column = dt_column
        self._period = period
        self._yscale = yscale
        self._figsize = figsize

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(column={self._column}, "
            f"dt_column={self._dt_column}, period={self._period}, "
            f"yscale={self._yscale}, figsize={self._figsize})"
        )

    def analyze(self, df: DataFrame) -> ColumnTemporalContinuousSection | EmptySection:
        logger.info(
            f"Analyzing the temporal continuous distribution of {self._column} | "
            f"datetime column: {self._dt_column} | period: {self._period}"
        )
        if self._column not in df:
            logger.info(
                "Skipping temporal continuous distribution analysis because the column "
                f"({self._column}) is not in the DataFrame: {sorted(df.columns)}"
            )
            return EmptySection()
        if self._dt_column not in df:
            logger.info(
                "Skipping temporal continuous distribution analysis because the datetime column "
                f"({self._dt_column}) is not in the DataFrame: {sorted(df.columns)}"
            )
            return EmptySection()
        return ColumnTemporalContinuousSection(
            column=self._column,
            df=df,
            dt_column=self._dt_column,
            period=self._period,
            yscale=self._yscale,
            figsize=self._figsize,
        )

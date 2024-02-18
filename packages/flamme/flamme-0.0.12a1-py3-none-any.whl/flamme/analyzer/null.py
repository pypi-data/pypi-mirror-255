from __future__ import annotations

__all__ = ["TemporalNullValueAnalyzer", "NullValueAnalyzer"]

import logging

import numpy as np
from pandas import DataFrame

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import EmptySection
from flamme.section.null import NullValueSection, TemporalNullValueSection

logger = logging.getLogger(__name__)


class NullValueAnalyzer(BaseAnalyzer):
    r"""Implements a null value analyzer.

    Args:
        figsize (``tuple`` , optional): Specifies the figure size in
            inches. The first dimension is the width and the second is
            the height. Default: ``None``

    Example usage:

    .. code-block:: pycon

        >>> import numpy as np
        >>> import pandas as pd
        >>> from flamme.analyzer import NullValueAnalyzer
        >>> analyzer = NullValueAnalyzer()
        >>> analyzer
        NullValueAnalyzer(figsize=None)
        >>> df = pd.DataFrame(
        ...     {
        ...         "int": np.array([np.nan, 1, 0, 1]),
        ...         "float": np.array([1.2, 4.2, np.nan, 2.2]),
        ...         "str": np.array(["A", "B", None, np.nan]),
        ...     }
        ... )
        >>> section = analyzer.analyze(df)
    """

    def __init__(self, figsize: tuple[float, float] | None = None) -> None:
        self._figsize = figsize

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(figsize={self._figsize})"

    def analyze(self, df: DataFrame) -> NullValueSection:
        logger.info("Analyzing the null value distribution of all columns...")
        return NullValueSection(
            columns=list(df.columns),
            null_count=df.isnull().sum().to_frame("count")["count"].to_numpy(),
            total_count=np.full((df.shape[1],), df.shape[0]),
            figsize=self._figsize,
        )


class TemporalNullValueAnalyzer(BaseAnalyzer):
    r"""Implements an analyzer to show the temporal distribution of null
    values.

    Args:
        dt_column (str): Specifies the datetime column used to analyze
            the temporal distribution.
        period (str): Specifies the temporal period e.g. monthly or
            daily.
        ncols (int, optional): Specifies the number of columns.
            Default: ``2``
        figsize (``tuple``, optional): Specifies the figure size in
            inches. The first dimension is the width and the second is
            the height. Default: ``(7, 5)``

    Example usage:

    .. code-block:: pycon

        >>> import numpy as np
        >>> import pandas as pd
        >>> from flamme.analyzer import TemporalNullValueAnalyzer
        >>> analyzer = TemporalNullValueAnalyzer("datetime", period="M")
        >>> analyzer
        TemporalNullValueAnalyzer(dt_column=datetime, period=M, ncols=2, figsize=(7, 5))
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
        dt_column: str,
        period: str,
        ncols: int = 2,
        figsize: tuple[float, float] = (7, 5),
    ) -> None:
        self._dt_column = dt_column
        self._period = period
        self._ncols = ncols
        self._figsize = figsize

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(dt_column={self._dt_column}, period={self._period}, "
            f"ncols={self._ncols}, figsize={self._figsize})"
        )

    def analyze(self, df: DataFrame) -> TemporalNullValueSection | EmptySection:
        logger.info(
            "Analyzing the temporal null value distribution of all columns | "
            f"datetime column: {self._dt_column} | period: {self._period}"
        )
        if self._dt_column not in df:
            logger.info(
                "Skipping monthly null value analysis because the datetime column "
                f"({self._dt_column}) is not in the DataFrame: {sorted(df.columns)}"
            )
            return EmptySection()
        return TemporalNullValueSection(
            df=df,
            dt_column=self._dt_column,
            period=self._period,
            ncols=self._ncols,
            figsize=self._figsize,
        )

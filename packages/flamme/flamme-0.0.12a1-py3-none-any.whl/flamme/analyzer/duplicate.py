from __future__ import annotations

__all__ = ["DuplicatedRowAnalyzer"]

import logging
from collections.abc import Sequence

from pandas import DataFrame

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import DuplicatedRowSection

logger = logging.getLogger(__name__)


class DuplicatedRowAnalyzer(BaseAnalyzer):
    r"""Implements an analyzer to show the number of duplicated rows.

    Args:
        columns (``Sequence`` or ``None``): Specifies the columns used
            to compute the duplicated rows. ``None`` means all the
            columns. Default: ``None``
        figsize (``tuple`` or ``None``, optional): Specifies the figure
            size in inches. The first dimension is the width and the
            second is the height. Default: ``None``

    Example usage:

    .. code-block:: pycon

        >>> import numpy as np
        >>> import pandas as pd
        >>> from flamme.analyzer import DuplicatedRowAnalyzer
        >>> analyzer = DuplicatedRowAnalyzer()
        >>> analyzer
        DuplicatedRowAnalyzer(columns=None, figsize=None)
        >>> df = pd.DataFrame(
        ...     {
        ...         "col1": np.array([0, 1, 0, 1]),
        ...         "col2": np.array([1, 0, 1, 0]),
        ...         "col3": np.array([1, 1, 1, 1]),
        ...     }
        ... )
        >>> section = analyzer.analyze(df)
    """

    def __init__(
        self,
        columns: Sequence[str] | None = None,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._columns = columns
        self._figsize = figsize

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(columns={self._columns}, figsize={self._figsize})"

    def analyze(self, df: DataFrame) -> DuplicatedRowSection:
        logger.info(f"Analyzing the duplicated rows section using the columns: {self._columns}")
        return DuplicatedRowSection(df=df, columns=self._columns, figsize=self._figsize)

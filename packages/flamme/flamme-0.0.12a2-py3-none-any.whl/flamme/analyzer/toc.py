from __future__ import annotations

__all__ = ["TableOfContentAnalyzer"]

import logging

from coola.utils import str_indent, str_mapping
from pandas import DataFrame

from flamme.analyzer.base import BaseAnalyzer, setup_analyzer
from flamme.section.toc import TableOfContentSection

logger = logging.getLogger(__name__)


class TableOfContentAnalyzer(BaseAnalyzer):
    r"""Implement a wrapper around an analyzer to add a table of content
    to the generated section report.

    Args:
        analyzer: Specifies the analyzer or its configuration.
        max_toc_depth: Specifies the maximum level to show in the
            table of content.

    Example usage:

    ```pycon
    >>> import numpy as np
    >>> import pandas as pd
    >>> from flamme.analyzer import TableOfContentAnalyzer, DuplicatedRowAnalyzer
    >>> analyzer = TableOfContentAnalyzer(DuplicatedRowAnalyzer())
    >>> analyzer
    TableOfContentAnalyzer(
      (analyzer): DuplicatedRowAnalyzer(columns=None, figsize=None)
      (max_toc_depth): 1
    )
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

    def __init__(
        self,
        analyzer: BaseAnalyzer | dict,
        max_toc_depth: int = 1,
    ) -> None:
        self._analyzer = setup_analyzer(analyzer)
        self._max_toc_depth = max_toc_depth

    def __repr__(self) -> str:
        args = str_indent(
            str_mapping({"analyzer": self._analyzer, "max_toc_depth": self._max_toc_depth})
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def analyze(self, df: DataFrame) -> TableOfContentSection:
        return TableOfContentSection(
            section=self._analyzer.analyze(df), max_toc_depth=self._max_toc_depth
        )

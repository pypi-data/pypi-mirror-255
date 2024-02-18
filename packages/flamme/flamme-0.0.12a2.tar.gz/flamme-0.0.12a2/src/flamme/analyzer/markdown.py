from __future__ import annotations

__all__ = ["MarkdownAnalyzer"]

from pandas import DataFrame

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import MarkdownSection


class MarkdownAnalyzer(BaseAnalyzer):
    r"""Implements an analyzer that adds a mardown string to the report..

    Example usage:

    .. code-block:: pycon

        >>> import numpy as np
        >>> import pandas as pd
        >>> from flamme.analyzer import MarkdownAnalyzer
        >>> analyzer = MarkdownAnalyzer(desc="hello cats!")
        >>> analyzer
        MarkdownAnalyzer()
        >>> df = pd.DataFrame({})
        >>> section = analyzer.analyze(df)
    """

    def __init__(self, desc: str) -> None:
        self._desc = str(desc)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def analyze(self, df: DataFrame) -> MarkdownSection:
        return MarkdownSection(desc=self._desc)

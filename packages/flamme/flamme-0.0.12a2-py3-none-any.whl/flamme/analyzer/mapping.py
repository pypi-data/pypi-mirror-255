from __future__ import annotations

__all__ = ["MappingAnalyzer"]

from collections.abc import Mapping

from coola.utils import str_indent, str_mapping
from pandas import DataFrame

from flamme.analyzer.base import BaseAnalyzer, setup_analyzer
from flamme.section import SectionDict


class MappingAnalyzer(BaseAnalyzer):
    r"""Implements an analyzer to analyze multiple analyzers.

    Args:
        analyzers (``Mapping``): Specifies the mappings to analyze.
            The key of each analyzer is used to organize the metrics
            and report.
        max_toc_depth: Specifies the maximum level to show in the
            table of content. Set this value to ``0`` to not show
            the table of content at the beginning of the section.

    Example usage:

    .. code-block:: pycon

        >>> import numpy as np
        >>> import pandas as pd
        >>> from flamme.analyzer import (
        ...     FilteredAnalyzer,
        ...     NullValueAnalyzer,
        ...     DuplicatedRowAnalyzer,
        ...     MappingAnalyzer,
        ... )
        >>> analyzer = MappingAnalyzer(
        ...     {"null": NullValueAnalyzer(), "duplicate": DuplicatedRowAnalyzer()}
        ... )
        >>> analyzer
        MappingAnalyzer(
          (null): NullValueAnalyzer(figsize=None)
          (duplicate): DuplicatedRowAnalyzer(columns=None, figsize=None)
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

    def __init__(
        self, analyzers: Mapping[str, BaseAnalyzer | dict], max_toc_depth: int = 0
    ) -> None:
        self._analyzers = {name: setup_analyzer(analyzer) for name, analyzer in analyzers.items()}
        self._max_toc_depth = max_toc_depth

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(\n  {str_indent(str_mapping(self._analyzers))}\n)"

    @property
    def analyzers(self) -> dict[str, BaseAnalyzer]:
        return self._analyzers

    def analyze(self, df: DataFrame) -> SectionDict:
        return SectionDict(
            sections={name: analyzer.analyze(df) for name, analyzer in self._analyzers.items()},
            max_toc_depth=self._max_toc_depth,
        )

    def add_analyzer(self, key: str, analyzer: BaseAnalyzer, replace_ok: bool = False) -> None:
        r"""Adds an analyzer to the current analyzer.

        Args:
            key: Specifies the key of the analyzer.
            analyzer: Specifies the analyzer to add.
            replace_ok: If ``False``, ``KeyError`` is raised if an
                analyzer with the same key exists. If ``True``,
                the new analyzer will replace the existing analyzer.

        Raises:
            KeyError: if an  analyzer with the same key exists.

        Example usage:

        ```pycon
        >>> import numpy as np
        >>> import pandas as pd
        >>> from flamme.analyzer import MappingAnalyzer, NullValueAnalyzer, DuplicatedRowAnalyzer
        >>> analyzer = MappingAnalyzer({"null": NullValueAnalyzer()})
        >>> analyzer.add_analyzer("duplicate", DuplicatedRowAnalyzer())
        >>> analyzer
        MappingAnalyzer(
          (null): NullValueAnalyzer(figsize=None)
          (duplicate): DuplicatedRowAnalyzer(columns=None, figsize=None)
        )
        >>> df = pd.DataFrame(
        ...     {
        ...         "int": np.array([np.nan, 1, 0, 1]),
        ...         "float": np.array([1.2, 4.2, np.nan, 2.2]),
        ...         "str": np.array(["A", "B", None, np.nan]),
        ...     }
        ... )
        >>> section = analyzer.analyze(df)

        ```
        """
        if key in self._analyzers and not replace_ok:
            raise KeyError(
                f"`{key}` is already used to register an analyzer. "
                "Use `replace_ok=True` to replace the analyzer"
            )
        self._analyzers[key] = analyzer

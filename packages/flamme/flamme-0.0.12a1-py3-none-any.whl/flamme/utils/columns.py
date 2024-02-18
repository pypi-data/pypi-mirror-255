from __future__ import annotations

__all__ = ["BaseColumn", "Column"]

from abc import abstractmethod

from coola.utils import str_indent, str_mapping

from flamme.analyzer.base import BaseAnalyzer, setup_analyzer
from flamme.transformer.series.base import (
    BaseSeriesTransformer,
    setup_series_transformer,
)


class BaseColumn:
    r"""Defines the column base class.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.utils.columns import Column
        >>> from flamme.analyzer import ColumnContinuousAnalyzer
        >>> from flamme.transformer.series import ToNumeric
        >>> column = Column(
        ...     can_be_null=True,
        ...     analyzer=ColumnContinuousAnalyzer(column="col"),
        ...     transformer=ToNumeric(),
        ... )
        >>> column
        Column(
          (can_be_null): True
          (analyzer): ColumnContinuousAnalyzer(column=col, nbins=None, yscale=auto, xmin=q0, xmax=q1, figsize=None)
          (transformer): ToNumericSeriesTransformer()
        )
        >>> analyzer = column.get_analyzer()
        >>> analyzer
        ColumnContinuousAnalyzer(column=col, nbins=None, yscale=auto, xmin=q0, xmax=q1, figsize=None)
        >>> transformer = column.get_transformer()
        >>> transformer
        ToNumericSeriesTransformer()
    """

    @abstractmethod
    def get_analyzer(self) -> BaseAnalyzer:
        r"""Gets the column analyzer.

        Returns:
        -------
            ``BaseAnalyzer``: The column analyzer.
        """

    @abstractmethod
    def get_transformer(self) -> BaseSeriesTransformer:
        r"""Gets the column transformer.

        Returns:
        -------
            ``BaseSeriesTransformer``: The column transformer.
        """


class Column(BaseColumn):
    r"""Defines the column base class.

    Args:
        can_be_null (bool): ``True`` if the column can have null
            values, otherwise ``False``.
        analyzer (``BaseAnalyzer`` or dict): Specifies the column
            analyzer or its configuration.
        transformer (``BaseSeriesTransformer`` or dict): Specifies
            the column  transformer or its configuration.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.utils.columns import Column
        >>> from flamme.analyzer import ColumnContinuousAnalyzer
        >>> from flamme.transformer.series import ToNumeric
        >>> column = Column(
        ...     can_be_null=True,
        ...     analyzer=ColumnContinuousAnalyzer(column="col"),
        ...     transformer=ToNumeric(),
        ... )
        >>> column
        Column(
          (can_be_null): True
          (analyzer): ColumnContinuousAnalyzer(column=col, nbins=None, yscale=auto, xmin=q0, xmax=q1, figsize=None)
          (transformer): ToNumericSeriesTransformer()
        )
        >>> analyzer = column.get_analyzer()
        >>> analyzer
        ColumnContinuousAnalyzer(column=col, nbins=None, yscale=auto, xmin=q0, xmax=q1, figsize=None)
        >>> transformer = column.get_transformer()
        >>> transformer
        ToNumericSeriesTransformer()
    """

    def __init__(
        self,
        can_be_null: bool,
        analyzer: BaseAnalyzer | dict,
        transformer: BaseSeriesTransformer | dict,
    ) -> None:
        self._can_be_null = bool(can_be_null)
        self._analyzer = setup_analyzer(analyzer)
        self._transformer = setup_series_transformer(transformer)

    def __repr__(self) -> str:
        args = str_indent(
            str_mapping(
                {
                    "can_be_null": self._can_be_null,
                    "analyzer": self._analyzer,
                    "transformer": self._transformer,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    @property
    def can_be_null(self) -> bool:
        r"""bool: ``True`` if the column can have null values, otherwise ``False``"""
        return self._can_be_null

    def get_analyzer(self) -> BaseAnalyzer:
        return self._analyzer

    def get_transformer(self) -> BaseSeriesTransformer:
        return self._transformer

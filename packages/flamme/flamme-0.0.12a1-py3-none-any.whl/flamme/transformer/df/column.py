from __future__ import annotations

__all__ = ["ColumnDataFrameTransformer"]

import logging

from coola.utils import str_indent, str_mapping
from pandas import DataFrame
from tqdm import tqdm

from flamme.transformer.df.base import BaseDataFrameTransformer
from flamme.transformer.series.base import BaseSeriesTransformer

logger = logging.getLogger(__name__)


class ColumnDataFrameTransformer(BaseDataFrameTransformer):
    r"""Implements a ``pandas.DataFrame`` transformer that applies
    ``pandas.Series`` transformers on some columns.

    Args:
        columns: Specifies the ``pandas.Series`` transformers.

    Example usage:

    ```pycon
    >>> import pandas as pd
    >>> from flamme.transformer.df import Column
    >>> from flamme.transformer.series import ToNumeric, StripString
    >>> transformer = Column({"col2": ToNumeric(), "col3": StripString()})
    >>> transformer
    ColumnDataFrameTransformer(
      (col2): ToNumericSeriesTransformer()
      (col3): StripStringSeriesTransformer()
      (ignore_missing): False
    )
    >>> df = pd.DataFrame(
    ...     {
    ...         "col1": [1, 2, 3, 4, 5],
    ...         "col2": ["1", "2", "3", "4", "5"],
    ...         "col3": [" a", "b ", " c ", "  d  ", "e"],
    ...     }
    ... )
    >>> df = transformer.transform(df)
    >>> df
       col1  col2 col3
    0     1     1    a
    1     2     2    b
    2     3     3    c
    3     4     4    d
    4     5     5    e

    ```
    """

    def __init__(
        self, columns: dict[str, BaseSeriesTransformer | dict], ignore_missing: bool = False
    ) -> None:
        self._columns = columns
        self._ignore_missing = bool(ignore_missing)

    def __repr__(self) -> str:
        columns = self._columns | {"ignore_missing": self._ignore_missing}
        args = f"\n  {str_indent(str_mapping(columns))}\n"
        return f"{self.__class__.__qualname__}({args})"

    @property
    def transformers(self) -> dict[str, BaseSeriesTransformer]:
        return self._columns

    def transform(self, df: DataFrame) -> DataFrame:
        for col, transformer in tqdm(self._columns.items(), desc="Transforming columns"):
            if col not in df:
                if self._ignore_missing:
                    logger.warning(
                        f"Skipping transformation for column {col} because the column is missing"
                    )
                else:
                    raise RuntimeError(
                        f"Column {col} is not in the DataFrame (columns:{sorted(df.columns)})"
                    )
            else:
                logger.info(f"Transforming column `{col}`...")
                df[col] = transformer.transform(df[col])
        return df

    def add_transformer(
        self, column: str, transformer: BaseSeriesTransformer, replace_ok: bool = False
    ) -> None:
        r"""Add a transformer to the current analyzer.

        Args:
            column: Specifies the column of the transformer.
            transformer: Specifies the transformer to add.
            replace_ok: If ``False``, ``KeyError`` is raised if a
                transformer with the same key exists. If ``True``,
                the new transformer will replace the existing
                transformer.

        Raises:
            KeyError: if a transformer with the same key exists.

        Example usage:

        ```pycon
        >>> import pandas as pd
        >>> from flamme.transformer.df import Column
        >>> from flamme.transformer.series import ToNumeric, StripString
        >>> transformer = Column({"col2": ToNumeric(), "col3": StripString()})
        >>> transformer
        ColumnDataFrameTransformer(
          (col2): ToNumericSeriesTransformer()
          (col3): StripStringSeriesTransformer()
          (ignore_missing): False
        )
        >>> transformer.add_transformer("col1", ToNumeric())
        >>> transformer
        ColumnDataFrameTransformer(
          (col2): ToNumericSeriesTransformer()
          (col3): StripStringSeriesTransformer()
          (col1): ToNumericSeriesTransformer()
          (ignore_missing): False
        )

        ```
        """
        if column in self._columns and not replace_ok:
            raise KeyError(
                f"`{column}` is already used to register a transformer. "
                "Use `replace_ok=True` to replace the transformer"
            )
        self._columns[column] = transformer

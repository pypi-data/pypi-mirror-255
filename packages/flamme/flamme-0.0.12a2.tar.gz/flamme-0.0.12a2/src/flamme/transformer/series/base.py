from __future__ import annotations

__all__ = ["BaseSeriesTransformer", "is_series_transformer_config", "setup_series_transformer"]

import logging
from abc import ABC

from objectory import AbstractFactory
from objectory.utils import is_object_config
from pandas import Series

logger = logging.getLogger(__name__)


class BaseSeriesTransformer(ABC, metaclass=AbstractFactory):
    r"""Defines the base class to transform a ``pandas.Series``.

    Example usage:

    .. code-block:: pycon

        >>> import pandas as pd
        >>> from flamme.transformer.series import ToNumeric
        >>> transformer = ToNumeric()
        >>> transformer
        ToNumericSeriesTransformer()
        >>> series = pd.Series(["1", "2", "3", "4", "5"])
        >>> series.dtype
        dtype('O')
        >>> series = transformer.transform(series)
        >>> series.dtype
        dtype('int64')
    """

    def transform(self, df: Series) -> Series:
        r"""Transforms a ``pandas.Series``.

        Args:
        ----
            df (``pandas.Series``): Specifies the ``pandas.Series``
                to transform.

        Returns:
        -------
            ``pandas.Series``: The transformed ``pandas.Series``.

        Example usage:

        .. code-block:: pycon

            >>> import pandas as pd
            >>> from flamme.transformer.series import ToNumeric
            >>> transformer = ToNumeric()
            >>> series = pd.Series(["1", "2", "3", "4", "5"])
            >>> series = transformer.transform(series)
            >>> series.dtype
            dtype('int64')
        """


def is_series_transformer_config(config: dict) -> bool:
    r"""Indicates if the input configuration is a configuration for a
    ``BaseSeriesTransformer``.

    This function only checks if the value of the key  ``_target_``
    is valid. It does not check the other values. If ``_target_``
    indicates a function, the returned type hint is used to check
    the class.

    Args:
        config (dict): Specifies the configuration to check.

    Returns:
        bool: ``True`` if the input configuration is a configuration
            for a ``BaseSeriesTransformer`` object.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.transformer.series import is_series_transformer_config
        >>> is_series_transformer_config({"_target_": "flamme.transformer.series.ToNumeric"})
        True
    """
    return is_object_config(config, BaseSeriesTransformer)


def setup_series_transformer(
    transformer: BaseSeriesTransformer | dict,
) -> BaseSeriesTransformer:
    r"""Sets up a ``pandas.Series`` transformer.

    The transformer is instantiated from its configuration
    by using the ``BaseSeriesTransformer`` factory function.

    Args:
        transformer (``BaseSeriesTransformer`` or dict): Specifies a
            ``pandas.Series`` transformer or its configuration.

    Returns:
        ``BaseSeriesTransformer``: An instantiated transformer.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.transformer.series import setup_series_transformer
        >>> transformer = setup_series_transformer(
        ...     {"_target_": "flamme.transformer.series.ToNumeric"}
        ... )
        >>> transformer
        ToNumericSeriesTransformer()
    """
    if isinstance(transformer, dict):
        logger.info("Initializing a series transformer from its configuration... ")
        transformer = BaseSeriesTransformer.factory(**transformer)
    if not isinstance(transformer, BaseSeriesTransformer):
        logger.warning(
            f"transformer is not a `BaseSeriesTransformer` (received: {type(transformer)})"
        )
    return transformer

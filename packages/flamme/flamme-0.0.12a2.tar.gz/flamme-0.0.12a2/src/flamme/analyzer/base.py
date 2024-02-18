from __future__ import annotations

__all__ = ["BaseAnalyzer", "setup_analyzer"]

import logging
from abc import ABC

from objectory import AbstractFactory
from objectory.utils import is_object_config
from pandas import DataFrame

from flamme.section import BaseSection

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC, metaclass=AbstractFactory):
    r"""Defines the base class to analyze a DataFrame.

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
        >>> analyzer.analyze(df)
    """

    def analyze(self, df: DataFrame) -> BaseSection:
        r"""Analyzes the data in a DataFrame.

        Args:
        ----
            df (``pandas.DataFrame``): Specifies the DataFrame with
                the data to analyze.

        Returns:
        -------
            ``BaseSection``: The section report.

        Example usage:

        .. code-block:: pycon

            >>> import numpy as np
            >>> import pandas as pd
            >>> from flamme.analyzer import NullValueAnalyzer
            >>> analyzer = NullValueAnalyzer()
            >>> df = pd.DataFrame(
            ...     {
            ...         "int": np.array([np.nan, 1, 0, 1]),
            ...         "float": np.array([1.2, 4.2, np.nan, 2.2]),
            ...         "str": np.array(["A", "B", None, np.nan]),
            ...     }
            ... )
            >>> analyzer.analyze(df)
        """


def is_analyzer_config(config: dict) -> bool:
    r"""Indicates if the input configuration is a configuration for a
    ``BaseAnalyzer``.

    This function only checks if the value of the key  ``_target_``
    is valid. It does not check the other values. If ``_target_``
    indicates a function, the returned type hint is used to check
    the class.

    Args:
        config (dict): Specifies the configuration to check.

    Returns:
        bool: ``True`` if the input configuration is a configuration
            for a ``BaseAnalyzer`` object.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.analyzer import is_analyzer_config
        >>> is_analyzer_config({"_target_": "flamme.analyzer.NullValueAnalyzer"})
        True
    """
    return is_object_config(config, BaseAnalyzer)


def setup_analyzer(
    analyzer: BaseAnalyzer | dict,
) -> BaseAnalyzer:
    r"""Sets up an analyzer.

    The analyzer is instantiated from its configuration
    by using the ``BaseAnalyzer`` factory function.

    Args:
        analyzer (``BaseAnalyzer`` or dict): Specifies an
            analyzer or its configuration.

    Returns:
        ``BaseAnalyzer``: An instantiated analyzer.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.analyzer import setup_analyzer
        >>> analyzer = setup_analyzer({"_target_": "flamme.analyzer.NullValueAnalyzer"})
        >>> analyzer
        NullValueAnalyzer(figsize=None)
    """
    if isinstance(analyzer, dict):
        logger.info("Initializing an analyzer from its configuration... ")
        analyzer = BaseAnalyzer.factory(**analyzer)
    if not isinstance(analyzer, BaseAnalyzer):
        logger.warning(f"analyzer is not a `BaseAnalyzer` (received: {type(analyzer)})")
    return analyzer

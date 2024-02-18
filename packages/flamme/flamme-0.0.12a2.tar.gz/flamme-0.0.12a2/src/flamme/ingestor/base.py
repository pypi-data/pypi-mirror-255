from __future__ import annotations

__all__ = ["BaseIngestor", "is_ingestor_config", "setup_ingestor"]

import logging
from abc import ABC

from objectory import AbstractFactory
from objectory.utils import is_object_config
from pandas import DataFrame

logger = logging.getLogger(__name__)


class BaseIngestor(ABC, metaclass=AbstractFactory):
    r"""Defines the base class to implement a DataFrame ingestor.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.ingestor import ParquetIngestor
        >>> ingestor = ParquetIngestor(path="/path/to/df.parquet")
        >>> ingestor
        ParquetIngestor(path=/path/to/df.parquet)
        >>> df = ingestor.ingest()  # doctest: +SKIP
    """

    def ingest(self) -> DataFrame:
        r"""Ingests a DataFrame.

        Returns:
            ``pandas.DataFrame``: The ingested DataFrame.

        Example usage:

        .. code-block:: pycon

            >>> from flamme.ingestor import ParquetIngestor
            >>> ingestor = ParquetIngestor(path="/path/to/df.parquet")
            >>> df = ingestor.ingest()  # doctest: +SKIP
        """


def is_ingestor_config(config: dict) -> bool:
    r"""Indicates if the input configuration is a configuration for a
    ``BaseIngestor``.

    This function only checks if the value of the key  ``_target_``
    is valid. It does not check the other values. If ``_target_``
    indicates a function, the returned type hint is used to check
    the class.

    Args:
        config (dict): Specifies the configuration to check.

    Returns:
        bool: ``True`` if the input configuration is a configuration
            for a ``BaseIngestor`` object.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.ingestor import is_ingestor_config
        >>> is_ingestor_config(
        ...     {"_target_": "flamme.ingestor.CsvIngestor", "path": "/path/to/data.csv"}
        ... )
        True
    """
    return is_object_config(config, BaseIngestor)


def setup_ingestor(
    ingestor: BaseIngestor | dict,
) -> BaseIngestor:
    r"""Sets up an ingestor.

    The ingestor is instantiated from its configuration
    by using the ``BaseIngestor`` factory function.

    Args:
        ingestor (``BaseIngestor`` or dict): Specifies an
            ingestor or its configuration.

    Returns:
        ``BaseIngestor``: An instantiated ingestor.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.ingestor import setup_ingestor
        >>> ingestor = setup_ingestor(
        ...     {"_target_": "flamme.ingestor.CsvIngestor", "path": "/path/to/data.csv"}
        ... )
        >>> ingestor
        CsvIngestor(path=/path/to/data.csv)
    """
    if isinstance(ingestor, dict):
        logger.info("Initializing an ingestor from its configuration... ")
        ingestor = BaseIngestor.factory(**ingestor)
    if not isinstance(ingestor, BaseIngestor):
        logger.warning(f"ingestor is not a `BaseIngestor` (received: {type(ingestor)})")
    return ingestor

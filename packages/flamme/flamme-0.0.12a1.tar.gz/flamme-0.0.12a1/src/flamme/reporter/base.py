from __future__ import annotations

__all__ = ["BaseReporter", "is_reporter_config", "setup_reporter"]

import logging
from abc import ABC

from objectory import AbstractFactory
from objectory.utils import is_object_config

logger = logging.getLogger(__name__)


class BaseReporter(ABC, metaclass=AbstractFactory):
    r"""Defines the base class to compute a HTML report.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.analyzer import NullValueAnalyzer
        >>> from flamme.ingestor import ParquetIngestor
        >>> from flamme.transformer.df import SequentialDataFrameTransformer
        >>> from flamme.reporter import Reporter
        >>> reporter = Reporter(
        ...     ingestor=ParquetIngestor("/path/to/data.parquet"),
        ...     transformer=SequentialDataFrameTransformer(transformers=[]),
        ...     analyzer=NullValueAnalyzer(),
        ...     report_path="/path/to/report.html",
        ... )
        >>> reporter
        Reporter(
          (ingestor): ParquetIngestor(path=/path/to/data.parquet)
          (transformer): SequentialDataFrameTransformer()
          (analyzer): NullValueAnalyzer(figsize=None)
          (report_path): /path/to/report.html
          (max_toc_depth): 6
        )
        >>> report = reporter.compute()  # doctest: +SKIP
    """

    def compute(self) -> None:
        r"""Computes a HTML report.

        Example usage:

        .. code-block:: pycon

            >>> from flamme.analyzer import NullValueAnalyzer
            >>> from flamme.ingestor import ParquetIngestor
            >>> from flamme.transformer.df import SequentialDataFrameTransformer
            >>> from flamme.reporter import Reporter
            >>> reporter = Reporter(
            ...     ingestor=ParquetIngestor("/path/to/data.parquet"),
            ...     transformer=SequentialDataFrameTransformer(transformers=[]),
            ...     analyzer=NullValueAnalyzer(figsize=None),
            ...     report_path="/path/to/report.html",
            ... )
            >>> report = reporter.compute()  # doctest: +SKIP
        """


def is_reporter_config(config: dict) -> bool:
    r"""Indicates if the input configuration is a configuration for a
    ``BaseReporter``.

    This function only checks if the value of the key  ``_target_``
    is valid. It does not check the other values. If ``_target_``
    indicates a function, the returned type hint is used to check
    the class.

    Args:
        config (dict): Specifies the configuration to check.

    Returns:
        bool: ``True`` if the input configuration is a configuration
            for a ``BaseReporter`` object.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.reporter import is_reporter_config
        >>> is_reporter_config(
        ...     {
        ...         "_target_": "flamme.reporter.Reporter",
        ...         "ingestor": {
        ...             "_target_": "flamme.ingestor.CsvIngestor",
        ...             "path": "/path/to/data.csv",
        ...         },
        ...         "transformer": {
        ...             "_target_": "flamme.transformer.df.ToNumeric",
        ...             "columns": ["col1", "col3"],
        ...         },
        ...         "analyzer": {"_target_": "flamme.analyzer.NullValueAnalyzer"},
        ...         "report_path": "/path/to/report.html",
        ...     }
        ... )
        True
    """
    return is_object_config(config, BaseReporter)


def setup_reporter(
    reporter: BaseReporter | dict,
) -> BaseReporter:
    r"""Sets up an reporter.

    The reporter is instantiated from its configuration
    by using the ``BaseReporter`` factory function.

    Args:
        reporter (``BaseReporter`` or dict): Specifies an
            reporter or its configuration.

    Returns:
        ``BaseReporter``: An instantiated reporter.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.reporter import setup_reporter
        >>> reporter = setup_reporter(
        ...     {
        ...         "_target_": "flamme.reporter.Reporter",
        ...         "ingestor": {
        ...             "_target_": "flamme.ingestor.CsvIngestor",
        ...             "path": "/path/to/data.csv",
        ...         },
        ...         "transformer": {
        ...             "_target_": "flamme.transformer.df.ToNumeric",
        ...             "columns": ["col1", "col3"],
        ...         },
        ...         "analyzer": {"_target_": "flamme.analyzer.NullValueAnalyzer"},
        ...         "report_path": "/path/to/report.html",
        ...     }
        ... )
        >>> reporter
        Reporter(
          (ingestor): CsvIngestor(path=/path/to/data.csv)
          (transformer): ToNumericDataFrameTransformer(columns=('col1', 'col3'))
          (analyzer): NullValueAnalyzer(figsize=None)
          (report_path): /path/to/report.html
          (max_toc_depth): 6
        )
    """
    if isinstance(reporter, dict):
        logger.info("Initializing an reporter from its configuration... ")
        reporter = BaseReporter.factory(**reporter)
    if not isinstance(reporter, BaseReporter):
        logger.warning(f"reporter is not a `BaseReporter` (received: {type(reporter)})")
    return reporter

from __future__ import annotations

__all__ = ["Reporter"]

import logging
from pathlib import Path

from coola.utils import str_indent, str_mapping

from flamme.analyzer.base import BaseAnalyzer, setup_analyzer
from flamme.ingestor.base import BaseIngestor, setup_ingestor
from flamme.reporter.base import BaseReporter
from flamme.reporter.utils import create_html_report
from flamme.transformer.df.base import (
    BaseDataFrameTransformer,
    setup_dataframe_transformer,
)
from flamme.utils.io import save_text
from flamme.utils.path import sanitize_path

logger = logging.getLogger(__name__)


class Reporter(BaseReporter):
    r"""Implements a simple reporter.

    Args:
        ingestor (``BaseIngestor`` or dict): Specifies the ingestor
            or its configuration.
        transformer (``BaseDataFrameTransformer`` or dict): Specifies
            a ``pandas.DataFrame`` transformer or its configuration.
        ingestor (``BaseAnalyzer`` or dict): Specifies the analyzer
            or its configuration.
        report_path (``Path`` or str): Specifies the path where to
            save the HTML report.
        max_toc_depth (int, optional): Specifies the maximum level
            to show in the table of content. Default: ``6``

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
        >>> report = reporter.compute()  # doctest: +SKIP
    """

    def __init__(
        self,
        ingestor: BaseIngestor | dict,
        transformer: BaseDataFrameTransformer | dict,
        analyzer: BaseAnalyzer | dict,
        report_path: Path | str,
        max_toc_depth: int = 6,
    ) -> None:
        self._ingestor = setup_ingestor(ingestor)
        logger.info(f"ingestor:\n{ingestor}")
        self._transformer = setup_dataframe_transformer(transformer)
        logger.info(f"transformer:\n{transformer}")
        self._analyzer = setup_analyzer(analyzer)
        logger.info(f"analyzer:\n{analyzer}")
        self._report_path = sanitize_path(report_path)
        self._max_toc_depth = int(max_toc_depth)

    def __repr__(self) -> str:
        args = str_indent(
            str_mapping(
                {
                    "ingestor": self._ingestor,
                    "transformer": self._transformer,
                    "analyzer": self._analyzer,
                    "report_path": self._report_path,
                    "max_toc_depth": self._max_toc_depth,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def compute(self) -> None:
        logger.info("Ingesting the DataFrame...")
        df = self._ingestor.ingest()
        logger.info(f"Transforming the DataFrame {df.shape}...")
        df = self._transformer.transform(df)
        logger.info(f"Analyzing the DataFrame {df.shape}...")
        section = self._analyzer.analyze(df)
        logger.info("Creating the HTML report...")
        report = create_html_report(
            toc=section.render_html_toc(max_depth=self._max_toc_depth),
            body=section.render_html_body(),
        )
        logger.info(f"Saving HTML report at {self._report_path}...")
        save_text(report, self._report_path)

from __future__ import annotations

__all__ = ["ClickHouseIngestor"]

import logging

from pandas import DataFrame

from flamme.ingestor.base import BaseIngestor
from flamme.utils.imports import (
    check_clickhouse_connect,
    is_clickhouse_connect_available,
)

if is_clickhouse_connect_available():  # pragma: no cover
    import clickhouse_connect


logger = logging.getLogger(__name__)


class ClickHouseIngestor(BaseIngestor):
    r"""Implement a clickhouse DataFrame ingestor.

    Args:
        query: Specifies the query to get the data.
        client_config: Specifies the clickhouse client configuration.
            Please check the documentation of
            ``clickhouse_connect.get_client`` to get more information.

    Example usage:

    ```pycon
    >>> from flamme.ingestor import ClickHouseIngestor
    >>> ingestor = ClickHouseIngestor(query="", client_config={})
    >>> ingestor
    ClickHouseIngestor()
    >>> df = ingestor.ingest()  # doctest: +SKIP

    ```
    """

    def __init__(self, query: str, client_config: dict) -> None:
        check_clickhouse_connect()
        self._query = str(query)
        self._client_config = client_config

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def ingest(self) -> DataFrame:
        logger.info(
            f"Ingesting data from clickhouse... \n"
            f"client configuration: {self._client_config}\n\n"
            "---------------------------------------------------------------------------------\n"
            f"query:\n{self._query}\n"
            "---------------------------------------------------------------------------------\n\n"
        )
        client = clickhouse_connect.get_client(**self._client_config)
        df = client.query_df(query=self._query).to_pandas().sort_index(axis=1)
        logger.info(f"Data ingested. DataFrame shape: {df.shape}")
        logger.info(f"number of unique column names: {len(set(df.columns)):,}")
        return df

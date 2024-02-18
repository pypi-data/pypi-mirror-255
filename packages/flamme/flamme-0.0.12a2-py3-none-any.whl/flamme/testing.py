r"""Define some utility functions for testing."""

from __future__ import annotations

__all__ = [
    "clickhouse_connect_available",
]

import pytest

from flamme.utils.imports import is_clickhouse_connect_available

clickhouse_connect_available = pytest.mark.skipif(
    not is_clickhouse_connect_available(), reason="Requires clickhouse_connect"
)

r"""Implement some utility functions to manage optional dependencies."""

from __future__ import annotations

__all__ = [
    "check_clickhouse_connect",
    "is_clickhouse_connect_available",
    "clickhouse_connect_available",
]

from importlib.util import find_spec
from typing import TYPE_CHECKING, Any

from coola.utils.imports import decorator_package_available

if TYPE_CHECKING:
    from collections.abc import Callable

##############################
#     clickhouse_connect     #
##############################


def is_clickhouse_connect_available() -> bool:
    r"""Indicate if the ``clickhouse_connect`` package is installed or
    not.

    Returns:
        ``True`` if ``clickhouse_connect`` is available otherwise
            ``False``.

    Example usage:

    ```pycon
    >>> from flamme.utils.imports import is_clickhouse_connect_available
    >>> is_clickhouse_connect_available()

    ```
    """
    return find_spec("clickhouse_connect") is not None


def check_clickhouse_connect() -> None:
    r"""Check if the ``clickhouse_connect`` package is installed.

    Raises:
        RuntimeError: if the ``clickhouse_connect`` package is not
            installed.

    Example usage:

    ```pycon
    >>> from flamme.utils.imports import check_clickhouse_connect
    >>> check_clickhouse_connect()

    ```
    """
    if not is_clickhouse_connect_available():
        msg = (
            "`clickhouse_connect` package is required but not installed. "
            "You can install `clickhouse_connect` package with the command:\n\n"
            "pip install clickhouse-connect\n"
        )
        raise RuntimeError(msg)


def clickhouse_connect_available(fn: Callable[..., Any]) -> Callable[..., Any]:
    r"""Implement a decorator to execute a function only if
    ``clickhouse_connect`` package is installed.

    Args:
        fn: Specifies the function to execute.

    Returns:
        A wrapper around ``fn`` if ``clickhouse_connect`` package is
            installed, otherwise ``None``.

    Example usage:

    ```pycon
    >>> from flamme.utils.imports import clickhouse_connect_available
    >>> @clickhouse_connect_available
    ... def my_function(n: int = 0) -> int:
    ...     return 42 + n
    ...
    >>> my_function()

    ```
    """
    return decorator_package_available(fn, is_clickhouse_connect_available)

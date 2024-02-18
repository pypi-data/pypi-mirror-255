from __future__ import annotations

__all__ = ["human_file_size", "sanitize_path", "find_files", "find_parquet_files"]

from collections.abc import Callable
from pathlib import Path
from urllib.parse import unquote, urlparse

from flamme.utils.format import human_byte


def human_file_size(path: Path | str, decimal: int = 2) -> str:
    r"""Gets a human-readable representation of a file size.

    Args:
        path (``pathlib.Path`` or str): Specifies the file.
        decimal (int, optional): Specifies the number of decimal
            digits. Default: ``2``

    Returns:
        str: The file size in a human-readable format.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.utils.path import human_file_size
        >>> human_file_size("README.md")
        '...B'
    """
    return human_byte(size=sanitize_path(path).stat().st_size, decimal=decimal)


def sanitize_path(path: Path | str) -> Path:
    r"""Sanitizes a given path.

    Args:
        path (``pathlib.Path`` or str): Specifies the path to
            sanitize.

    Returns:
        ``pathlib.Path``: The sanitized path.

    Example usage:

    .. code-block:: pycon

        >>> from pathlib import Path
        >>> from flamme.utils.path import sanitize_path
        >>> sanitize_path("something")
        PosixPath('.../something')
        >>> sanitize_path("")
        PosixPath('...')
        >>> sanitize_path(Path("something"))
        PosixPath('.../something')
        >>> sanitize_path(Path("something/./../"))
        PosixPath('...')
    """
    if isinstance(path, str):
        # Use urlparse to parse file URI: https://stackoverflow.com/a/15048213
        path = Path(unquote(urlparse(path).path))
    return path.expanduser().resolve()


def find_files(
    path: Path | str, filter_fn: Callable[[Path], bool], recursive: bool = True
) -> list[Path]:
    r"""Finds the path of all the tar files in a given path.

    This function does not check if a path is a symbolic link so be
    careful if you are using a path with symbolic links.

    Args:
        path: Specifies the path where to look for the parquet files.
        filter_fn: Specifies the path filtering function. The function
            should return ``True`` for the path to find, and
            ``False`` otherwise.
        recursive: Specifies if it should also check the sub-folders.

    Returns:
        The tuple of path of parquet files.

    Example usage:

    ```pycon
    >>> from pathlib import Path
    >>> from flamme.utils.path import find_files
    >>> find_files(Path("something"), filter_fn=lambda path: path.name.endswith(".txt"))
    [...]

    ```
    """
    path = sanitize_path(path)
    paths = [path] if path.is_file() else path.glob("**/*" if recursive else "*")
    return list(filter(filter_fn, [p for p in paths if p.is_file()]))


def find_parquet_files(path: Path | str, recursive: bool = True) -> list[Path]:
    r"""Finds the path of all the parquet files in a given path.

    This function does not check if a path is a symbolic link so be
    careful if you are using a path with symbolic links.

    Args:
        path: Specifies the path where to look for the parquet files.
        recursive: Specifies if it should also check the sub-folders.

    Returns:
        The tuple of path of parquet files.

    Example usage:

    ```pycon
    >>> from pathlib import Path
    >>> from flamme.utils.path import find_parquet_files
    >>> find_parquet_files(Path("something"))
    [...]

    ```
    """
    return find_files(
        path=path, filter_fn=lambda path: path.name.endswith(".parquet"), recursive=recursive
    )

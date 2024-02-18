from __future__ import annotations

__all__ = ["load_text", "save_text"]

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_text(path: Path) -> str:
    r"""Reads the data from a given text file.

    Args:
        path (``pathlib.Path``): Specifies the path where to the text
            file.

    Returns:
        The data from the text file.

    Example usage:

    .. code-block:: pycon

        >>> from pathlib import Path
        >>> from flamme.utils.io import load_text
        >>> data = load_text(Path("/path/to/data.txt"))  # xdoctest: +SKIP()
    """
    logger.debug(f"read {path}")
    with Path.open(path) as file:
        data = file.read()
    return data


def save_text(to_save: str, path: Path) -> None:
    r"""Saves the given data in a text file.

    Args:
        to_save: Specifies the data to write in a text file.
        path (``pathlib.Path``): Specifies the path where to write the
            text file.

    Example usage:

    .. code-block:: pycon

        >>> from pathlib import Path
        >>> from flamme.utils.io import save_text
        >>> save_text("abc", Path("/path/to/data.txt"))  # xdoctest: +SKIP()
    """
    logger.debug(f"write data in a text file: {path}")
    path.parents[0].mkdir(exist_ok=True, parents=True)
    # Save to tmp, then commit by moving the file in case the job gets
    # interrupted while writing the file
    tmp_path = path.parents[0].joinpath(f"{path.name}.tmp")
    with Path.open(tmp_path, mode="w") as file:
        file.write(to_save)
    tmp_path.rename(path)

from __future__ import annotations

__all__ = ["find_range"]

import numpy as np


def find_range(
    values: np.ndarray,
    xmin: float | int | str | None = None,
    xmax: float | int | str | None = None,
) -> tuple[float | int, float | int]:
    r"""Finds a range of value.

    Args:
        values (``numpy.ndarray``): Specifies the values used to find
            the quantiles.
        xmin (float or str or None, optional): Specifies the minimum
            value of the range or its associated quantile.
            ``q0.1`` means the 10% quantile. ``0`` is the minimum
            value and ``1`` is the maximum value. Default: ``None``
        xmax (float or str or None, optional): Specifies the maximum
            value of the range or its associated quantile.
            ``q0.9`` means the 90% quantile. ``0`` is the minimum
            value and ``1`` is the maximum value. Default: ``None``

    Returns:
        tuple: The range of values in the format ``(min, max)``.

    Example usage:

    .. code-block:: pycon

        >>> import numpy as np
        >>> from flamme.utils.range import find_range
        >>> data = np.arange(101)
        >>> find_range(data)
        (0, 100)
        >>> find_range(data, xmin=5, xmax=50)
        (5, 50)
        >>> find_range(data, xmin="q0.1", xmax="q0.9")
        (10.0, 90.0)
    """
    if xmin is None:
        xmin = np.nanmin(values).item()
    if xmax is None:
        xmax = np.nanmax(values).item()
    q = [float(x[1:]) for x in [xmin, xmax] if isinstance(x, str)]
    quantiles = np.nanquantile(values, q)
    if isinstance(xmin, str):
        xmin = quantiles[0]
    if isinstance(xmax, str):
        xmax = quantiles[-1]
    return (xmin, xmax)

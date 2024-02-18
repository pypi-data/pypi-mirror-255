from __future__ import annotations

__all__ = ["figure2html"]

import base64
import io
import math

from matplotlib import pyplot as plt
from matplotlib.axes import Axes


def figure2html(fig: plt.Figure, close_fig: bool = False) -> str:
    r"""Converts a matplotlib figure to a string that can be used in a
    HTML file.

    Args:
        fig (``Figure``): Specifies the figure to convert.
        close_fig (``bool``, optional): If ``True``, the figure is
            closed after it is converted to HTML format.
            Default: ``False``

    Returns:
        str: The converted figure to a string.

    Example usage:

    .. code-block:: pycon

        >>> from matplotlib import pyplot as plt
        >>> from flamme.utils.figure import figure2html
        >>> fig, ax = plt.subplots()
        >>> string = figure2html(fig)
    """
    fig.tight_layout()
    img = io.BytesIO()
    fig.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    data = base64.b64encode(img.getvalue()).decode("utf-8")
    if close_fig:
        plt.close(fig)
    return f'<img src="data:image/png;charset=utf-8;base64, {data}">'


def readable_xticklabels(
    ax: Axes,
    max_num_xticks: int = 100,
    xticklabel_max_len: int = 20,
    xticklabel_min: int = 10,
) -> None:
    r"""Updates the tick labels to make them easier to read, in
    particular if the tick labels are dense.

    Args:
        ax (``matplotlib.axes.Axes``):
        max_num_xticks (int, optional): Specifies the maximum number
            of ticks to show in the figure. Default: ``100``
        xticklabel_max_len (int, optional): If a tick label has a
            length greater than this value, the tick labels are
            rotated vertically. Default: ``20``
        xticklabel_min (int, optional): If the number of ticks is
            lower than this number the tick labels are rotated
            vertically. Default: ``10``

    Example usage:

    .. code-block:: pycon

        >>> import numpy as np
        >>> from matplotlib import pyplot as plt
        >>> from flamme.utils.figure import readable_xticklabels
        >>> fig, ax = plt.subplots()
        >>> ax.hist(np.arange(10), bins=10)
        >>> readable_xticklabels(ax)
    """
    xticks = ax.get_xticks()
    if len(xticks) > max_num_xticks:
        n = math.ceil(len(xticks) / max_num_xticks)
        xticks = xticks[::n]
        ax.set_xticks(xticks)
    if len(xticks) > xticklabel_min or any(
        [len(str(label)) > xticklabel_max_len for label in ax.get_xticklabels()]
    ):
        ax.tick_params(axis="x", labelrotation=90)

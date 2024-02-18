from __future__ import annotations

__all__ = ["ColumnContinuousAdvancedSection"]

import logging
from collections.abc import Sequence

import numpy as np
from jinja2 import Template
from matplotlib import pyplot as plt
from pandas import Series

from flamme.section.base import BaseSection
from flamme.section.continuous import (
    add_cdf_plot,
    create_boxplot_figure,
    create_histogram_figure,
    create_stats_table,
)
from flamme.section.utils import (
    GO_TO_TOP,
    auto_yscale_continuous,
    compute_statistics,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)
from flamme.utils.figure import figure2html, readable_xticklabels
from flamme.utils.range import find_range

logger = logging.getLogger(__name__)


class ColumnContinuousAdvancedSection(BaseSection):
    r"""Implements a section that analyzes a continuous distribution of
    values.

    Args:
        series: Specifies the series/column to analyze.
        column: Specifies the column name.
        nbins: Specifies the number of bins in the histogram.
        yscale: Specifies the y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'/'symlog'`` scale is chosen based
            on the distribution.
        figsize: Specifies the figure size in inches. The first
            dimension is the width and the second is the height.
    """

    def __init__(
        self,
        series: Series,
        column: str,
        nbins: int | None = None,
        yscale: str = "auto",
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._series = series
        self._column = column
        self._nbins = nbins
        self._yscale = yscale
        self._figsize = figsize

    @property
    def column(self) -> str:
        return self._column

    @property
    def yscale(self) -> str:
        return self._yscale

    @property
    def nbins(self) -> int | None:
        return self._nbins

    @property
    def series(self) -> Series:
        return self._series

    @property
    def figsize(self) -> tuple[float, float] | None:
        r"""tuple: The individual figure size in pixels. The first
        dimension is the width and the second is the height."""
        return self._figsize

    def get_statistics(self) -> dict[str, float | int]:
        return compute_statistics(self._series)

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info(f"Rendering the continuous distribution of {self._column}")
        stats = self.get_statistics()
        null_values_pct = (
            f"{100 * stats['num_nulls'] / stats['count']:.2f}" if stats["count"] > 0 else "N/A"
        )
        return Template(self._create_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "column": self._column,
                "table": create_stats_table(stats=stats, column=self._column),
                "total_values": f"{stats['count']:,}",
                "unique_values": f"{stats['nunique']:,}",
                "null_values": f"{stats['num_nulls']:,}",
                "null_values_pct": null_values_pct,
                "full_histogram": self._create_full_histogram(stats),
                "iqr_histogram": self._create_iqr_histogram(),
                "full_boxplot": self._create_full_boxplot(),
            }
        )

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        return render_html_toc(number=number, tags=tags, depth=depth, max_depth=max_depth)

    def _create_template(self) -> str:
        return """
<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">
This section analyzes the discrete distribution of values for column <em>{{column}}</em>.

<ul>
  <li> total values: {{total_values}} </li>
  <li> number of unique values: {{unique_values}} </li>
  <li> number of null values: {{null_values}} / {{total_values}} ({{null_values_pct}}%) </li>
</ul>

<p style="margin-top: 1rem;">
<b> Analysis of the distribution </b>

{{full_histogram}}
{{full_boxplot}}
{{table}}
<p style="margin-top: 1rem;">

<p style="margin-top: 1rem;">
<b> Analysis of distribution in the inter-quartile range (IQR) </b>

{{iqr_histogram}}

"""

    def _create_full_boxplot(self) -> str:
        return create_boxplot_figure(
            series=self._series,
            xmin="q0",
            xmax="q1",
            figsize=self._figsize,
        )

    def _create_full_histogram(self, stats: dict) -> str:
        return create_histogram_figure(
            series=self._series,
            column=self._column,
            stats=stats,
            nbins=self._nbins,
            xmin="q0",
            xmax="q1",
            yscale=self._yscale,
            figsize=self._figsize,
        )

    def _create_iqr_histogram(self) -> str:
        return create_histogram_range_figure(
            series=self._series,
            column=self._column,
            nbins=self._nbins,
            xmin="q0.25",
            xmax="q0.75",
            yscale=self._yscale,
            figsize=self._figsize,
        )


def create_histogram_range_figure(
    series: Series,
    column: str,
    nbins: int | None = None,
    yscale: str = "auto",
    xmin: float | str | None = None,
    xmax: float | str | None = None,
    figsize: tuple[float, float] | None = None,
) -> str:
    r"""Creates the HTML code of a histogram figure.

    Args:
        series: Specifies the series/column to analyze.
        column: Specifies the column name.
        nbins: Specifies the number of bins in the histogram.
        yscale: Specifies the y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'`` scale is chosen based on the
            distribution.
        xmin: Specifies the minimum value of the range or its
            associated quantile. ``q0.1`` means the 10% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        xmax: Specifies the maximum value of the range or its
            associated quantile. ``q0.9`` means the 90% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        figsize: Specifies the figure size in inches. The first
            dimension is the width and the second is the height.

    Returns:
        str: The HTML code of the figure.
    """
    array = series.to_numpy()
    if array.size == 0:
        return "<span>&#9888;</span> No figure is generated because the column is empty"
    xmin, xmax = find_range(array, xmin=xmin, xmax=xmax)
    array_range = array[np.logical_and(array >= xmin, array <= xmax)]
    fig, ax = plt.subplots(figsize=figsize)
    ax.hist(array_range, bins=nbins, range=[xmin, xmax], color="tab:blue", alpha=0.9)
    if xmin < xmax:
        ax.set_xlim(xmin, xmax)
    readable_xticklabels(ax, max_num_xticks=100)
    ax.set_title(f"Distribution of values for column {column}")
    ax.set_ylabel("Number of occurrences")
    if yscale == "auto":
        yscale = auto_yscale_continuous(array=array_range, nbins=nbins)
    ax.set_yscale(yscale)
    add_cdf_plot(ax, array=array, nbins=nbins, xmin=xmin, xmax=xmax)
    return figure2html(fig, close_fig=True)

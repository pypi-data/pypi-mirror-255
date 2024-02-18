from __future__ import annotations

__all__ = ["ColumnTemporalContinuousSection"]

import logging
from collections.abc import Sequence

import numpy as np
import pandas as pd
from jinja2 import Template
from matplotlib import pyplot as plt
from pandas import DataFrame

from flamme.section.base import BaseSection
from flamme.section.utils import (
    GO_TO_TOP,
    auto_yscale_continuous,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)
from flamme.utils.figure import figure2html, readable_xticklabels
from flamme.utils.mathnan import remove_nan

logger = logging.getLogger(__name__)


class ColumnTemporalContinuousSection(BaseSection):
    r"""Implements a section that analyzes the temporal distribution of a
    column with continuous values.

    Args:
        df: Specifies the DataFrame to analyze.
        column: Specifies the column to analyze.
        dt_column: Specifies the datetime column used to analyze
            the temporal distribution.
        period: Specifies the temporal period e.g. monthly or daily.
        yscale: Specifies the y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'/'symlog'`` scale is chosen based
            on the distribution.
        figsize: Specifies the figure size in inches. The first
            dimension is the width and the second is the height.
    """

    def __init__(
        self,
        df: DataFrame,
        column: str,
        dt_column: str,
        period: str,
        yscale: str = "auto",
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._df = df
        self._column = column
        self._dt_column = dt_column
        self._period = period
        self._yscale = yscale
        self._figsize = figsize

    @property
    def column(self) -> str:
        return self._column

    @property
    def dt_column(self) -> str:
        return self._dt_column

    @property
    def yscale(self) -> str:
        return self._yscale

    @property
    def period(self) -> str:
        return self._period

    @property
    def figsize(self) -> tuple[float, float] | None:
        r"""tuple: The individual figure size in pixels. The first
        dimension is the width and the second is the height."""
        return self._figsize

    def get_statistics(self) -> dict:
        return {}

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info(
            f"Rendering the temporal continuous distribution of {self._column} | "
            f"datetime column: {self._dt_column} | period: {self._period}"
        )
        return Template(self._create_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "column": self._column,
                "dt_column": self._dt_column,
                "period": self._period,
                "figure": create_temporal_figure(
                    df=self._df,
                    column=self._column,
                    dt_column=self._dt_column,
                    period=self._period,
                    yscale=self._yscale,
                    figsize=self._figsize,
                ),
                "table": create_temporal_table(
                    df=self._df,
                    column=self._column,
                    dt_column=self._dt_column,
                    period=self._period,
                ),
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
This section analyzes the temporal distribution of column <em>{{column}}</em>
by using the column <em>{{dt_column}}</em>.

{{figure}}

{{table}}
<p style="margin-top: 1rem;">
"""


def create_temporal_figure(
    df: DataFrame,
    column: str,
    dt_column: str,
    period: str,
    yscale: str = "auto",
    figsize: tuple[float, float] | None = None,
) -> str:
    r"""Creates a HTML representation of a figure with the temporal value
    distribution.

    Args:
        df: Specifies the DataFrame to analyze.
        column: Specifies the column to analyze.
        dt_column: Specifies the datetime column used to analyze
            the temporal distribution.
        period: Specifies the temporal period e.g. monthly or daily.
        yscale: Specifies the y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'/'symlog'`` scale is chosen based
            on the distribution.
        figsize: Specifies the figure size in inches. The first
            dimension is the width and the second is the height.

    Returns:
        The HTML representation of the figure.
    """
    if df.shape[0] == 0:
        return "<span>&#9888;</span> No figure is generated because the column is empty"
    array = df[column].to_numpy(dtype=float)
    df = df[[column, dt_column]].copy()
    df[dt_column] = df[dt_column].dt.to_period(period).astype(str)
    df_group = (
        df.groupby(dt_column)[column]
        .apply(list)
        .reset_index(name=column)
        .sort_values(by=[dt_column])
    )

    data = [remove_nan(x) for x in df_group[column].tolist()]
    labels = df_group[dt_column].tolist()
    fig, ax = plt.subplots(figsize=figsize)
    ax.boxplot(
        data,
        notch=True,
        vert=True,
        widths=0.7,
        patch_artist=True,
        boxprops=dict(facecolor="lightblue"),
    )
    ax.set_ylim(np.nanmin(array), np.nanmax(array))
    ax.set_xticks(np.arange(len(labels)), labels=labels)
    ax.set_title(f"Distribution of values for column {column}")
    if yscale == "auto":
        yscale = auto_yscale_continuous(array=array, nbins=100)
    ax.set_yscale(yscale)
    readable_xticklabels(ax)
    return figure2html(fig, close_fig=True)


def create_temporal_table(df: DataFrame, column: str, dt_column: str, period: str) -> str:
    r"""Creates a HTML representation of a table with some statistics
    about the temporal value distribution.

    Args:
        df (``DataFrame``): Specifies the DataFrame to analyze.
        column (str): Specifies the column to analyze.
        dt_column (str): Specifies the datetime column used to analyze
            the temporal distribution.
        period (str): Specifies the temporal period e.g. monthly or
            daily.

    Returns:
        str: The HTML representation of the table.
    """
    if df.shape[0] == 0:
        return "<span>&#9888;</span> No table is generated because the column is empty"
    df = df[[column, dt_column]].copy()
    dt_col = "__datetime__"
    df[dt_col] = df[dt_column].dt.to_period(period)
    df_stats = (
        df.groupby(dt_col)[column]
        .agg(
            [
                "count",
                "mean",
                "median",
                "min",
                "max",
                "std",
                ("q01", lambda x: x.quantile(0.01)),
                ("q05", lambda x: x.quantile(0.05)),
                ("q10", lambda x: x.quantile(0.1)),
                ("q25", lambda x: x.quantile(0.25)),
                ("q75", lambda x: x.quantile(0.75)),
                ("q90", lambda x: x.quantile(0.9)),
                ("q95", lambda x: x.quantile(0.95)),
                ("q99", lambda x: x.quantile(0.99)),
            ]
        )
        .sort_index()
    )

    rows = []
    for row in df_stats.itertuples():
        rows.append(create_temporal_table_row(row))
    return Template(
        """
<details>
    <summary>Statistics per period</summary>

    <p>The following table shows some statistics for each period of column {{column}}.

    <table class="table table-hover table-responsive w-auto" >
        <thead class="thead table-group-divider">
            <tr>
                <th>column</th>
                <th>count</th>
                <th>mean</th>
                <th>std</th>
                <th>min</th>
                <th>quantile 1%</th>
                <th>quantile 5%</th>
                <th>quantile 10%</th>
                <th>quantile 25%</th>
                <th>median</th>
                <th>quantile 75%</th>
                <th>quantile 90%</th>
                <th>quantile 95%</th>
                <th>quantile 99%</th>
                <th>max</th>
            </tr>
        </thead>
        <tbody class="tbody table-group-divider">
            {{rows}}
            <tr class="table-group-divider"></tr>
        </tbody>
    </table>
</details>
"""
    ).render({"rows": "\n".join(rows), "column": column, "period": period})


def create_temporal_table_row(row: pd.core.frame.Pandas) -> str:
    r"""Creates the HTML code of a new table row.

    Args:
        row: Specifies a DataFrame row.

    Returns:
        The HTML code of a row.
    """
    return Template(
        """<tr>
    <th>{{datetime}}</th>
    <td {{num_style}}>{{count}}</td>
    <td {{num_style}}>{{mean}}</td>
    <td {{num_style}}>{{std}}</td>
    <td {{num_style}}>{{min}}</td>
    <td {{num_style}}>{{q01}}</td>
    <td {{num_style}}>{{q05}}</td>
    <td {{num_style}}>{{q10}}</td>
    <td {{num_style}}>{{q25}}</td>
    <td {{num_style}}>{{median}}</td>
    <td {{num_style}}>{{q75}}</td>
    <td {{num_style}}>{{q90}}</td>
    <td {{num_style}}>{{q95}}</td>
    <td {{num_style}}>{{q99}}</td>
    <td {{num_style}}>{{max}}</td>
</tr>"""
    ).render(
        {
            "num_style": 'style="text-align: right;"',
            "datetime": row.Index,
            "count": f"{row.count:,}",
            "mean": f"{row.mean:,.4f}",
            "median": f"{row.median:,.4f}",
            "min": f"{row.min:,.4f}",
            "max": f"{row.max:,.4f}",
            "std": f"{row.std:,.4f}",
            "q01": f"{row.q01:,.4f}",
            "q05": f"{row.q05:,.4f}",
            "q10": f"{row.q10:,.4f}",
            "q25": f"{row.q25:,.4f}",
            "q75": f"{row.q75:,.4f}",
            "q90": f"{row.q90:,.4f}",
            "q95": f"{row.q95:,.4f}",
            "q99": f"{row.q99:,.4f}",
        }
    )

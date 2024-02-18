from __future__ import annotations

__all__ = ["NullValueSection", "TemporalNullValueSection"]

import logging
import math
from collections.abc import Sequence

import numpy as np
from jinja2 import Template
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from pandas import DataFrame

from flamme.section.base import BaseSection
from flamme.section.utils import (
    GO_TO_TOP,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)
from flamme.utils.figure import figure2html, readable_xticklabels

logger = logging.getLogger(__name__)


class NullValueSection(BaseSection):
    r"""Implements a section that analyzes the number of null values.

    Args:
        columns (``Sequence``): Specifies the column names.
        null_count (``numpy.ndarray``): Specifies the number of null
            values for each column.
        total_count (``numpy.ndarray``): Specifies the total number
            of values for each column.
        figsize (``tuple`` or ``None``, optional): Specifies the figure
            size in inches. The first dimension is the width and the
            second is the height. Default: ``None``
    """

    def __init__(
        self,
        columns: Sequence[str],
        null_count: np.ndarray,
        total_count: np.ndarray,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._columns = tuple(columns)
        self._null_count = null_count.flatten().astype(int)
        self._total_count = total_count.flatten().astype(int)
        self._figsize = figsize

        if len(self._columns) != self._null_count.shape[0]:
            raise RuntimeError(
                f"columns ({len(self._columns):,}) and null_count ({self._null_count.shape[0]:,}) "
                "do not match"
            )
        if len(self._columns) != self._total_count.shape[0]:
            raise RuntimeError(
                f"columns ({len(self._columns):,}) and total_count "
                f"({self._total_count.shape[0]:,}) do not match"
            )

    @property
    def columns(self) -> tuple[str, ...]:
        r"""Tuple: The columns used to compute the duplicated rows."""
        return self._columns

    @property
    def null_count(self) -> np.ndarray:
        r"""``numpy.ndarray``: The number of null values for each
        column."""
        return self._null_count

    @property
    def total_count(self) -> np.ndarray:
        r"""``numpy.ndarray``: The total number of values for each
        column."""
        return self._total_count

    @property
    def figsize(self) -> tuple[float, float] | None:
        r"""tuple: The individual figure size in pixels. The first
        dimension is the width and the second is the height."""
        return self._figsize

    def get_statistics(self) -> dict:
        return {
            "columns": self._columns,
            "null_count": tuple(self._null_count.tolist()),
            "total_count": tuple(self._total_count.tolist()),
        }

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info("Rendering the null value distribution of all columns...")
        return Template(self._create_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "table_alpha": self._create_table(sort_by="column"),
                "table_sort": self._create_table(sort_by="null"),
                "bar_figure": self._create_bar_figure(),
                "num_columns": f"{len(self._columns):,}",
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
This section analyzes the number and proportion of null values for the {{num_columns}}
columns.
In the following histogram, the columns are sorted by ascending order of null values.


{{bar_figure}}

<details>
    <summary>Show analysis per column</summary>

    <p style="margin-top: 1rem;">
    The following tables show the number and proportion of null values for the {{num_columns}}
    columns.
    The background color of the row indicates the proportion of missing values:
    dark blues indicates more missing values than light blues.

    <div class="container-fluid">
        <div class="row align-items-start">
            <div class="col align-self-center">
                <p><b>Columns sorted by alphabetical order</b></p>

                {{table_alpha}}

            </div>
            <div class="col">
                <p><b>Columns sorted by ascending order of missing values</b></p>

                {{table_sort}}

            </div>
        </div>
    </div>
</details>
<p style="margin-top: 1rem;">
"""

    def _create_bar_figure(self) -> str:
        df = self._get_dataframe().sort_values(by="null")
        fig, ax = plt.subplots(figsize=self._figsize)
        labels = df["column"].tolist()
        ax.bar(x=labels, height=df["null"].to_numpy(), color="tab:blue")
        if labels:
            ax.set_xlim(-0.5, len(labels) - 0.5)
        readable_xticklabels(ax, max_num_xticks=100)
        ax.set_xlabel("column")
        ax.set_ylabel("number of null values")
        ax.set_title("number of null values per column")
        return figure2html(fig, close_fig=True)

    def _create_table(self, sort_by: str) -> str:
        df = self._get_dataframe().sort_values(by=sort_by)
        rows = "\n".join(
            [
                create_table_row(column=column, null_count=null_count, total_count=total_count)
                for column, null_count, total_count in zip(
                    df["column"].to_numpy(), df["null"].to_numpy(), df["total"].to_numpy()
                )
            ]
        )
        return Template(
            """
<table class="table table-hover table-responsive w-auto" >
    <thead class="thead table-group-divider">
        <tr>
            <th>column</th>
            <th>null pct</th>
            <th>null count</th>
            <th>total count</th>
        </tr>
    </thead>
    <tbody class="tbody table-group-divider">
        {{rows}}
        <tr class="table-group-divider"></tr>
    </tbody>
</table>
"""
        ).render({"rows": rows})

    def _get_dataframe(self) -> DataFrame:
        return DataFrame(
            {"column": self._columns, "null": self._null_count, "total": self._total_count}
        )


def create_table_row(column: str, null_count: int, total_count: int) -> str:
    r"""Creates the HTML code of a new table row.

    Args:
        column (str): Specifies the column name.
        null_count (int): Specifies the number of null values.
        total_count (int): Specifies the total number of rows.

    Returns:
        str: The HTML code of a row.
    """
    pct = null_count / total_count
    return Template(
        """<tr>
    <th style="background-color: rgba(0, 191, 255, {{null_pct}})">{{column}}</th>
    <td {{num_style}}>{{null_pct}}</td>
    <td {{num_style}}>{{null_count}}</td>
    <td {{num_style}}>{{total_count}}</td>
</tr>"""
    ).render(
        {
            "num_style": f'style="text-align: right; background-color: rgba(0, 191, 255, {pct})"',
            "column": column,
            "null_count": f"{null_count:,}",
            "null_pct": f"{pct:.4f}",
            "total_count": f"{total_count:,}",
        }
    )


class TemporalNullValueSection(BaseSection):
    r"""Implements a section to analyze the temporal distribution of null
    values.

    Args:
        df (``pandas.DataFrame``): Specifies the DataFrame to analyze.
        dt_column (str): Specifies the datetime column used to analyze
            the temporal distribution.
        period (str): Specifies the temporal period e.g. monthly or
            daily.
        ncols (int, optional): Specifies the number of columns.
            Default: ``2``
        figsize (``tuple``, optional): Specifies the figure size in
            inches. The first dimension is the width and the second is
            the height. Default: ``(7, 5)``
    """

    def __init__(
        self,
        df: DataFrame,
        dt_column: str,
        period: str,
        ncols: int = 2,
        figsize: tuple[float, float] = (7, 5),
    ) -> None:
        self._df = df
        self._dt_column = dt_column
        self._period = period
        self._ncols = ncols
        self._figsize = figsize

    @property
    def df(self) -> DataFrame:
        r"""``pandas.DataFrame``: The DataFrame to analyze."""
        return self._df

    @property
    def dt_column(self) -> str:
        r"""str: The datetime column."""
        return self._dt_column

    @property
    def period(self) -> str:
        r"""str: The temporal period used to analyze the data."""
        return self._period

    @property
    def ncols(self) -> int:
        r"""int: The number of columns to show the figures."""
        return self._ncols

    @property
    def figsize(self) -> tuple[float, float] | None:
        r"""Tuple or ``None``: The individual figure size in pixels.

        The first dimension is the width and the second is the height.
        """
        return self._figsize

    def get_statistics(self) -> dict:
        return {}

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info(
            "Rendering the temporal null value distribution of all columns | "
            f"datetime column: {self._dt_column} | period: {self._period}"
        )
        return Template(self._create_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "column": self._dt_column,
                "figure": create_temporal_null_figure(
                    df=self._df,
                    dt_column=self._dt_column,
                    period=self._period,
                    ncols=self._ncols,
                    figsize=self._figsize,
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
This section analyzes the monthly distribution of null values.
The column <em>{{column}}</em> is used as the temporal column.

{{figure}}
"""


def create_temporal_null_figure(
    df: DataFrame,
    dt_column: str,
    period: str,
    ncols: int = 2,
    figsize: tuple[float, float] = (7, 5),
) -> str:
    r"""Creates a HTML representation of a figure with the temporal null
    value distribution.

    Args:
        df (``DataFrame``): Specifies the DataFrame to analyze.
        dt_column (str): Specifies the datetime column used to analyze
            the temporal distribution.
        period (str): Specifies the temporal period e.g. monthly or
            daily.
        ncols (int, optional): Specifies the number of columns.
            Default: ``2``
        figsize (``tuple``, optional): Specifies the figure size in
            inches. The first dimension is the width and the second is
            the height. Default: ``(7, 5)``

    Returns:
        str: The HTML representation of the figure.
    """
    if df.shape[0] == 0:
        return ""
    columns = sorted([col for col in df.columns if col != dt_column])
    nrows = math.ceil(len(columns) / ncols)
    fig, axes = plt.subplots(
        nrows=nrows, ncols=ncols, figsize=(figsize[0] * ncols, figsize[1] * nrows)
    )

    for i, column in enumerate(columns):
        if ncols > 1:
            ax = axes[i // ncols, i % ncols]
        else:
            ax = axes[i]
        ax.set_title(f"column: {column}")

        num_nulls, total, labels = prepare_data(
            df=df, column=column, dt_column=dt_column, period=period
        )
        plot_temporal_null_total(ax=ax, labels=labels, num_nulls=num_nulls, total=total)
        readable_xticklabels(ax, max_num_xticks=100 // ncols)

    return figure2html(fig, close_fig=True)


def plot_temporal_null_total(
    ax: Axes, num_nulls: np.ndarray, total: np.ndarray, labels: list
) -> None:
    color = "tab:blue"
    x = np.arange(len(labels))
    ax.set_ylabel("number of null/total values", color=color)
    ax.tick_params(axis="y", labelcolor=color)
    ax.bar(x=x, height=total, color="tab:cyan", alpha=0.5, label="total")
    ax.bar(x=x, height=num_nulls, color=color, alpha=0.8, label="null")
    ax.legend()

    ax2 = ax.twinx()
    color = "black"
    ax2.set_ylabel("percentage", color=color)
    ax2.tick_params(axis="y", labelcolor=color)
    ax2.plot(x, num_nulls / total, "o-", color=color)

    ax.set_xticks(x, labels=labels)
    ax.set_xlim(-0.5, len(labels) - 0.5)


def prepare_data(
    df: DataFrame,
    column: str,
    dt_column: str,
    period: str,
) -> tuple[np.ndarray, np.ndarray, list]:
    r"""Prepares the data to create the figure and table.

    Args:
        df (``pandas.DataFrame``): Specifies the DataFrame to analyze.
        column (str): Specifies the column to analyze.
        dt_column (str): Specifies the datetime column used to analyze
            the temporal distribution.
        period (str): Specifies the temporal period e.g. monthly or
            daily.

    Returns:
        tuple: A tuple with 3 values. The first value is a numpy NDArray
            that contains the number of null values per period. The
            second value is a numpy NDArray that contains the total
            number of values. The third value is a list that contains
            the label of each period.

    Example usage:

    .. code-block:: pycon

        >>> import pandas as pd
        >>> from flamme.section.null_temp_col import prepare_data
        >>> num_nulls, total, labels = prepare_data(
        ...     df=pd.DataFrame(
        ...         {
        ...             "col": np.array([np.nan, 1, 0, 1]),
        ...             "datetime": pd.to_datetime(
        ...                 ["2020-01-03", "2020-02-03", "2020-03-03", "2020-04-03"]
        ...             ),
        ...         }
        ...     ),
        ...     column="col",
        ...     dt_column="datetime",
        ...     period="M",
        ... )
        >>> num_nulls
        array([1, 0, 0, 0])
        >>> total
        array([1, 1, 1, 1])
        >>> labels
        ['2020-01', '2020-02', '2020-03', '2020-04']
    """
    df = df[[column, dt_column]].copy()
    dt_col = "__datetime__"
    df[dt_col] = df[dt_column].dt.to_period(period)

    null_col = f"__{column}_isnull__"
    df.loc[:, null_col] = df.loc[:, column].isnull()

    df_num_nulls = df.groupby(dt_col)[null_col].sum().sort_index()
    df_total = df.groupby(dt_col)[null_col].count().sort_index()
    labels = [str(dt) for dt in df_num_nulls.index]
    return df_num_nulls.to_numpy().astype(int), df_total.to_numpy().astype(int), labels

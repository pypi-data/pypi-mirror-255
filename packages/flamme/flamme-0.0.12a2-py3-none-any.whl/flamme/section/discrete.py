from __future__ import annotations

__all__ = ["ColumnDiscreteSection"]

import logging
from collections import Counter
from collections.abc import Sequence

import numpy as np
from jinja2 import Template
from matplotlib import pyplot as plt

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


class ColumnDiscreteSection(BaseSection):
    r"""Implements a section that analyzes a discrete distribution of
    values.

    Args:
        counter: Specifies the counter that represents the discrete
            distribution.
        null_values: Specifies the number of null values.
        column: Specifies the column name.
        max_rows: Specifies the maximum number of rows to show in the
            table.
        yscale: Specifies the y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'`` scale is chosen based on the
            distribution.
        figsize: Specifies the figure size in inches. The first
            dimension is the width and the second is the height.
    """

    def __init__(
        self,
        counter: Counter,
        null_values: int = 0,
        column: str = "N/A",
        max_rows: int = 20,
        yscale: str = "auto",
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._counter = counter
        self._null_values = null_values
        self._column = column
        self._max_rows = int(max_rows)
        self._yscale = yscale
        self._figsize = figsize

        self._total = sum(self._counter.values())

    @property
    def figsize(self) -> tuple[float, float] | None:
        r"""The individual figure size in pixels.

        The first dimension is the width and the second is the height.
        """
        return self._figsize

    @property
    def yscale(self) -> str:
        return self._yscale

    def get_statistics(self) -> dict:
        most_common = [(value, count) for value, count in self._counter.most_common() if count > 0]
        return {
            "most_common": most_common,
            "nunique": len(most_common),
            "total": self._total,
        }

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info(f"Rendering the discrete distribution of {self._column}")
        stats = self.get_statistics()
        null_values_pct = (
            f"{100 * self._null_values / stats['total']:.2f}" if stats["total"] > 0 else "N/A"
        )
        return Template(self._create_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "column": self._column,
                "total_values": f"{stats['total']:,}",
                "unique_values": f"{stats['nunique']:,}",
                "null_values": f"{self._null_values:,}",
                "null_values_pct": null_values_pct,
                "figure": self._create_figure(),
                "table": self._create_table(),
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

{{figure}}
{{table}}
<p style="margin-top: 1rem;">
"""

    def _create_figure(self) -> str:
        if self._total == 0:
            return "<span>&#9888;</span> No figure is generated because the column is empty"
        most_common = [(value, count) for value, count in self._counter.most_common() if count > 0]
        fig = create_histogram(
            column=self._column,
            labels=[str(value) for value, _ in most_common],
            counts=[count for _, count in most_common],
            yscale=self._yscale,
            figsize=self._figsize,
        )
        return Template(
            r"""
<p style="margin-top: 1rem;">
<b>Distribution of values in column {{column}}</b>

<p>The values in the figure below are sorted by decreasing order of number of occurrences.

{{figure}}
"""
        ).render({"figure": fig, "column": self._column})

    def _create_table(self) -> str:
        if self._total == 0:
            return "<span>&#9888;</span> No table is generated because the column is empty"

        most_common = self._counter.most_common(self._max_rows)
        rows_head = "\n".join(
            [create_table_row(column=col, count=count) for col, count in most_common]
        )
        lest_common = self._counter.most_common()[-self._max_rows :][::-1]
        rows_tail = "\n".join(
            [create_table_row(column=col, count=count) for col, count in lest_common]
        )
        return Template(
            """
<details>
    <summary>Show head and tail values</summary>

    <div class="row">
      <div class="col">
        <p style="margin-top: 1rem;">
        <b>Head: {{max_values}} most common values in column <em>{{column}}</em></b>
        <table class="table table-hover table-responsive w-auto" >
            <thead class="thead table-group-divider">
                <tr>
                    <th>column</th>
                    <th>count</th>
                </tr>
            </thead>
            <tbody class="tbody table-group-divider">
                {{rows_head}}
                <tr class="table-group-divider"></tr>
            </tbody>
        </table>
      </div>
      <div class="col">
        <p style="margin-top: 1rem;">
        <b>Tail: {{max_values}} least common values in column <em>{{column}}</em></b>
        <table class="table table-hover table-responsive w-auto" >
            <thead class="thead table-group-divider">
                <tr>
                    <th>column</th>
                    <th>count</th>
                </tr>
            </thead>
            <tbody class="tbody table-group-divider">
                {{rows_tail}}
                <tr class="table-group-divider"></tr>
            </tbody>
        </table>
      </div>
    </div>
</details>
"""
        ).render(
            {
                "max_values": len(most_common),
                "rows_head": rows_head,
                "rows_tail": rows_tail,
                "column": self._column,
            }
        )


def create_histogram(
    column: str,
    labels: list[str],
    counts: list[int],
    yscale: str = "auto",
    figsize: tuple[float, float] | None = None,
) -> str:
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(labels))
    ax.bar(x, counts, width=0.9 if len(labels) < 50 else 1, color="tab:blue")
    if yscale == "auto":
        yscale = "log" if (max(counts) / min(counts)) >= 50 else "linear"
    ax.set_yscale(yscale)
    ax.set_xticks(x, labels=labels)
    readable_xticklabels(ax, max_num_xticks=100)
    ax.set_xlim(-0.5, len(labels) - 0.5)
    ax.set_ylabel("Number of occurrences")
    ax.set_title(f"Number of occurrences for each value of {column}")
    return figure2html(fig, close_fig=True)


def create_table_row(column: str, count: int) -> str:
    r"""Creates the HTML code of a new table row.

    Args:
        column (str): Specifies the column name.
        count (int): Specifies the count for the column.

    Returns:
        str: The HTML code of a row.
    """
    return Template("""<tr><th>{{column}}</th><td {{num_style}}>{{count}}</td></tr>""").render(
        {"num_style": 'style="text-align: right;"', "column": column, "count": f"{count:,}"}
    )

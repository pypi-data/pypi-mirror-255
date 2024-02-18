from __future__ import annotations

__all__ = ["DuplicatedRowSection"]

import logging
from collections.abc import Sequence

from jinja2 import Template
from matplotlib import pyplot as plt
from pandas import DataFrame

from flamme.section.base import BaseSection
from flamme.section.utils import (
    GO_TO_TOP,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)
from flamme.utils.figure import figure2html

logger = logging.getLogger(__name__)


class DuplicatedRowSection(BaseSection):
    r"""Implements a section to analyze the number of duplicated rows.

    Args:
        df (``pandas.DataFrame``): Specifies the DataFrame to analyze.
        columns (``Sequence`` or ``None``): Specifies the columns used
            to compute the duplicated rows. ``None`` means all the
            columns. Default: ``None``
        figsize (``tuple`` or ``None``, optional): Specifies the figure
            size in inches. The first dimension is the width and the
            second is the height. Default: ``None``
    """

    def __init__(
        self,
        df: DataFrame,
        columns: Sequence[str] | None = None,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._df = df
        self._columns = columns if columns is None else tuple(columns)
        self._figsize = figsize

    @property
    def df(self) -> DataFrame:
        r"""``pandas.DataFrame``: The DataFrame to analyze."""
        return self._df

    @property
    def columns(self) -> tuple[str, ...] | None:
        r"""Tuple or ``None``: The columns used to compute the
        duplicated rows."""
        return self._columns

    @property
    def figsize(self) -> tuple[float, float] | None:
        r"""tuple: The individual figure size in pixels. The first
        dimension is the width and the second is the height."""
        return self._figsize

    def get_statistics(self) -> dict:
        df_no_duplicate = self._df.drop_duplicates(subset=self._columns)
        return {"num_rows": self._df.shape[0], "num_unique_rows": df_no_duplicate.shape[0]}

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info(f"Rendering the duplicated rows section using the columns: {self._columns}")
        stats = self.get_statistics()
        columns = self._df.columns if self._columns is None else self._columns
        return Template(self._create_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "columns": ", ".join(columns),
                "num_columns": f"{len(columns):,}",
                "table": create_duplicate_table(
                    num_rows=stats["num_rows"], num_unique_rows=stats["num_unique_rows"]
                ),
                "figure": create_duplicate_histogram(
                    num_rows=stats["num_rows"],
                    num_unique_rows=stats["num_unique_rows"],
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
This section shows the number of duplicated rows using {{num_columns}} columns:
<em>{{columns}}</em>.

{{table}}

{{figure}}
<p style="margin-top: 1rem;">
"""


def create_duplicate_histogram(
    num_rows: int, num_unique_rows: int, figsize: tuple[float, float] | None = None
) -> str:
    fig, ax = plt.subplots(figsize=figsize)
    x = list(range(3))
    ax.bar(x, [num_rows, num_unique_rows, num_rows - num_unique_rows], color="tab:blue")
    ax.set_xticks(x, labels=["total", "unique", "duplicate"])
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylabel("Number of occurrences")
    ax.set_title("Analysis of the number of duplicate rows")
    return figure2html(fig, close_fig=True)


def create_duplicate_table(num_rows: int, num_unique_rows: int) -> str:
    r"""Creates a table with information about duplicated rows.

    Args:
        num_rows (int): Specifies the number of rows.
        num_unique_rows (int): Specifies the number of unique rows.

    Returns:
        str: The HTML representation of the table.
    """
    num_duplicated_rows = num_rows - num_unique_rows
    pct_unique_rows = num_unique_rows / num_rows if num_rows else float("nan")
    pct_duplicated_rows = 1.0 - pct_unique_rows
    return Template(
        """
<table class="table table-hover table-responsive w-auto" >
<thead class="thead table-group-divider">
    <tr>
        <th>number of rows</th>
        <th>number of unique rows</th>
        <th>number of duplicated rows</th>
    </tr>
</thead>
<tbody class="tbody table-group-divider">
    <tr>
        <td {{num_style}}>{{num_rows}}</td>
        <td {{num_style}}>{{num_unique_rows}} ({{pct_unique_rows}}%)</td>
        <td {{num_style}}>{{num_duplicated_rows}} ({{pct_duplicated_rows}}%)</td>
    </tr>
    <tr class="table-group-divider"></tr>
</tbody>
</table>
"""
    ).render(
        {
            "num_style": 'style="text-align: right;"',
            "num_rows": f"{num_rows:,}",
            "num_unique_rows": f"{num_unique_rows:,}",
            "num_duplicated_rows": f"{num_duplicated_rows:,}",
            "pct_unique_rows": f"{100 * pct_unique_rows:.2f}",
            "pct_duplicated_rows": f"{100 * pct_duplicated_rows:.2f}",
        }
    )

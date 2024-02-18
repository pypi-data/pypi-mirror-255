from __future__ import annotations

__all__ = ["DataTypeSection"]

import copy
import logging
from collections.abc import Sequence

import numpy as np
from jinja2 import Template

from flamme.section.base import BaseSection
from flamme.section.utils import (
    GO_TO_TOP,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)

logger = logging.getLogger(__name__)


class DataTypeSection(BaseSection):
    r"""Implements a section that analyzes the data type of each column.

    Args:
        dtypes (``dict``): Specifies the data type for each column.
        types (``dict``): Specifies the types of the values in each
            column. A column can contain multiple types. The keys are
            the column names.
    """

    def __init__(self, dtypes: dict[str, np.dtype], types: dict[str, set]) -> None:
        self._dtypes = dtypes
        self._types = types

        dtkeys = set(self._dtypes.keys())
        tkeys = set(self._types.keys())
        if dtkeys != tkeys:
            raise RuntimeError(
                f"The keys of dtypes and types do not match:\n"
                f"({len(dtkeys)}): {dtkeys}\n"
                f"({len(tkeys)}): {tkeys}\n"
            )

    def get_statistics(self) -> dict:
        return copy.deepcopy(self._types)

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        return Template(self._create_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "table": self._create_table(),
            }
        )

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        logger.info("Rendering the data types report...")
        return render_html_toc(number=number, tags=tags, depth=depth, max_depth=max_depth)

    def _create_template(self) -> str:
        return """
<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">
This section analyzes the values types for each column.

<ul>
  <li> <b>data type</b>: is the pandas data type used to represent the column </li>
  <li> <b>types</b>: are the real object types for the objects in the column </li>
</ul>

{{table}}
"""

    def _create_table(self) -> str:
        columns = sorted(self._types.keys())
        rows = "\n".join(
            [
                create_table_row(column=col, types=self._types[col], dtype=self._dtypes[col])
                for col in columns
            ]
        )
        return Template(
            """
<table class="table table-hover table-responsive w-auto" >
    <thead class="thead table-group-divider">
        <tr>
            <th>column</th>
            <th>data type</th>
            <th>types</th>
        </tr>
    </thead>
    <tbody class="tbody table-group-divider">
        {{rows}}
        <tr class="table-group-divider"></tr>
    </tbody>
</table>
"""
        ).render({"rows": rows})


def create_table_row(column: str, dtype: np.dtype, types: set) -> str:
    r"""Creates the HTML code of a new table row.

    Args:
        column (str): Specifies the column name.
        dtype (``numpy.ndtype``): Specifies the column data type.
        types (set): Specifies the types in th column.

    Returns:
        str: The HTML code of a row.
    """
    types = sorted([str(t).replace("<", "&lt;").replace(">", "&gt;") for t in types])
    return Template(
        """<tr>
    <th>{{column}}</th>
    <td>{{dtype}}</td>
    <td>{{types}}</td>
</tr>"""
    ).render({"column": column, "dtype": dtype, "types": ", ".join(types)})

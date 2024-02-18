from __future__ import annotations

__all__ = ["EmptySection"]

from collections.abc import Sequence

from flamme.section.base import BaseSection


class EmptySection(BaseSection):
    r"""Implements an empty section.

    This section is implemented to deal with missing columns or to skip
    some analyses.
    """

    def get_statistics(self) -> dict:
        return {}

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        return ""

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        return ""

from __future__ import annotations

__all__ = ["TableOfContentSection"]

from collections.abc import Sequence

from flamme.section.base import BaseSection


class TableOfContentSection(BaseSection):
    r"""Implement a wrapper section that generates a table of content
    before the section.

    Args:
        section: Specifies the section.
        max_toc_depth: Specifies the maximum level to show in the
            table of content.
    """

    def __init__(self, section: BaseSection, max_toc_depth: int = 1) -> None:
        self._section = section
        self._max_toc_depth = int(max_toc_depth)

    def get_statistics(self) -> dict:
        return self._section.get_statistics()

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        toc = self._section.render_html_toc(
            number=number, tags=tags, depth=0, max_depth=self._max_toc_depth
        )
        body = self._section.render_html_body(number=number, tags=tags, depth=depth)
        return f"{toc}\n\n{body}"

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        return self._section.render_html_toc(
            number=number, tags=tags, depth=depth, max_depth=max_depth
        )

from __future__ import annotations

__all__ = ["SectionDict"]

from collections.abc import Sequence

from coola.utils import str_indent

from flamme.section.base import BaseSection
from flamme.section.utils import (
    GO_TO_TOP,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)


class SectionDict(BaseSection):
    r"""Implements a section to manage a dictionary of sections.

    Args:
        sections: Specifies the dictionary of sections.
        max_toc_depth: Specifies the maximum level to show in the
            table of content. Set this value to ``0`` to not show
            the table of content at the beginning of the section.
    """

    def __init__(self, sections: dict[str, BaseSection], max_toc_depth: int = 0) -> None:
        self._sections = sections
        self._max_toc_depth = max_toc_depth

    @property
    def sections(self) -> dict[str, BaseSection]:
        return self._sections

    @property
    def max_toc_depth(self) -> int:
        return self._max_toc_depth

    def get_statistics(self) -> dict:
        return {name: section.get_statistics() for name, section in self._sections.items()}

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        report = []
        if tags:
            report.append(
                f'<h{valid_h_tag(depth+1)} id="{tags2id(tags)}">{number} '
                f"{tags2title(tags)} </h{valid_h_tag(depth+1)}>"
            )
            report.extend([GO_TO_TOP, '<p style="margin-top: 1rem;">'])

        if self._max_toc_depth > 0:
            report.append(
                self._render_html_toc_subsections(
                    number=number, tags=tags, depth=0, max_depth=self._max_toc_depth
                )
            )

        for i, (name, section) in enumerate(self._sections.items()):
            report.append(
                section.render_html_body(
                    number=f"{number}{i + 1}.", tags=list(tags) + [name], depth=depth + 1
                )
            )
        return "\n".join(report)

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        if depth >= max_depth:
            return ""
        toc = []
        if tags:
            toc.append(render_html_toc(number=number, tags=tags, depth=depth, max_depth=max_depth))
        subtoc = self._render_html_toc_subsections(tags=tags, depth=depth + 1, max_depth=max_depth)
        if subtoc:
            toc.append(subtoc)
        return "\n".join(toc)

    def _render_html_toc_subsections(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        subtoc = []
        for i, (name, section) in enumerate(self._sections.items()):
            line = section.render_html_toc(
                number=f"{number}{i + 1}.",
                tags=list(tags) + [name],
                depth=depth,
                max_depth=max_depth,
            )
            if line:
                subtoc.append(f"  {str_indent(line)}")
        if subtoc:
            subtoc.insert(0, "<ul>")
            subtoc.append("</ul>")
        return "\n".join(subtoc)

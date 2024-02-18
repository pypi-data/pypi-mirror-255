from __future__ import annotations

__all__ = ["BaseSection"]

from abc import ABC, abstractmethod
from collections.abc import Sequence


class BaseSection(ABC):
    r"""Defines the base class to manage sections."""

    @abstractmethod
    def get_statistics(self) -> dict:
        r"""Computes the statistics associated to the section.

        Returns:
        -------
            dict: The statistics.
        """

    @abstractmethod
    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        r"""Renders the HTML body associated to the section.

        Args:
        ----
            number (str, optional): Specifies the section number.
                Default: ""
            tags (``Sequence``, optional): Specifies the tags
                associated to the section. Default: ``()``
            depth (int, optional): Specifies the depth in the report.
                Default: ``0``

        Returns:
        -------
            str: The HTML body associated to the section.
        """

    @abstractmethod
    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        r"""Renders the HTML table of content (TOC) associated to the
        section.

        Args:
        ----
            number (str, optional): Specifies the section number
                associated to the section. Default: ""
            tags (``Sequence``, optional): Specifies the tags
                associated to the section. Default: ``()``
            depth (int, optional): Specifies the depth in the report.
                Default: ``0``

        Returns:
        -------
            str: The HTML table of content associated to the section.
        """

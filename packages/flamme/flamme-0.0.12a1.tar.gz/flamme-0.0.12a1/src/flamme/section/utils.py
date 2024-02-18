from __future__ import annotations

__all__ = [
    "auto_yscale_continuous",
    "compute_statistics",
    "render_html_toc",
    "tags2id",
    "tags2title",
    "valid_h_tag",
]

from collections.abc import Sequence

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, skew

from flamme.utils.array import nonnan

GO_TO_TOP = '<a href="#">Go to top</a>'


def tags2id(tags: Sequence[str]) -> str:
    r"""Converts a sequence of tags to a string that can be used as ID in
    a HTML file.

    Args:
        tags (``Sequence``): Specifies the sequence of tags.

    Returns:
        str: The generated ID from the tags.
    """
    return "-".join(tags).replace(" ", "-").lower()


def tags2title(tags: Sequence[str]) -> str:
    r"""Converts a sequence of tags to a string that can be used as
    title.

    Args:
        tags (``Sequence``): Specifies the sequence of tags.

    Returns:
        str: The generated title from the tags.
    """
    return " | ".join(tags[::-1])


def valid_h_tag(index: int) -> int:
    r"""Computes a valid number of a h HTML tag.

    Args:
        index (int): Specifies the original value.

    Returns:
        int: A valid value.
    """
    return max(1, min(6, index))


def render_html_toc(
    number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
) -> str:
    r"""Renders the HTML table of content (TOC) associated to the
    section.

    Args:
        number (str, optional): Specifies the section number
            associated to the section. Default: ""
        tags (``Sequence``, optional): Specifies the tags
            associated to the section. Default: ``()``
        depth (int, optional): Specifies the depth in the report.
            Default: ``0``

    Returns:
        str: The HTML table of content associated to the section.
    """
    if depth >= max_depth:
        return ""
    tag = tags[-1] if tags else ""
    return f'<li><a href="#{tags2id(tags)}">{number} {tag}</a></li>'


def auto_yscale_continuous(array: np.ndarray, nbins: int | None = None) -> str:
    r"""Find a good scale for y-axis based on the data distribution.

    Args:
        array: Specifies the data to use to find the scale.
        nbins: Specifies the number of bins in the histogram.

    Returns:
        The scale for y-axis.

    Example usage:

    ```pycon
    >>> import numpy as np
    >>> from flamme.section.utils import auto_yscale_continuous
    >>> auto_yscale_continuous(np.arange(100))
    linear

    ```
    """
    if nbins is None:
        nbins = 100
    array = nonnan(array)
    counts = np.histogram(array, bins=nbins)[0]
    nonzero_count = [c for c in counts if c > 0]
    if len(nonzero_count) <= 2 or (max(nonzero_count) / max(min(nonzero_count), 1)) < 50:
        return "linear"
    if np.nanmin(array) <= 0.0:
        return "symlog"
    return "log"


def compute_statistics(data: pd.Series | np.ndarray) -> dict[str, float | int]:
    r"""Compute several descriptive statistics for the input data.

    Args:
        data: Specifies the data to analyze.

    Returns:
        The descriptive statistics for the input data.

    Example usage:

    ```pycon
    >>> import numpy as np
    >>> from flamme.section.utils import compute_statistics
    >>> compute_statistics(np.arange(101))
    {'count': 101, 'num_nulls': 0, 'nunique': 101, 'mean': 50.0, 'std': 29.30...,
     'skewness': 0.0, 'kurtosis': -1.20..., 'min': 0.0, 'q001': 0.1, 'q01': 1.0,
     'q05': 5.0, 'q10': 10.0, 'q25': 25.0, 'median': 50.0, 'q75': 75.0, 'q90': 90.0,
     'q95': 95.0, 'q99': 99.0, 'q999': 99.9, 'max': 100.0, '>0': 100, '<0': 0, '=0': 1,
     'num_non_nulls': 101}

    ```
    """
    series = data if isinstance(data, pd.Series) else pd.Series(data)
    stats = {
        "count": int(series.shape[0]),
        "num_nulls": int(series.isnull().sum()),
        "nunique": series.nunique(dropna=False),
        "mean": float("nan"),
        "std": float("nan"),
        "skewness": float("nan"),
        "kurtosis": float("nan"),
        "min": float("nan"),
        "q001": float("nan"),
        "q01": float("nan"),
        "q05": float("nan"),
        "q10": float("nan"),
        "q25": float("nan"),
        "median": float("nan"),
        "q75": float("nan"),
        "q90": float("nan"),
        "q95": float("nan"),
        "q99": float("nan"),
        "q999": float("nan"),
        "max": float("nan"),
        ">0": (series > 0).sum().item(),
        "<0": (series < 0).sum().item(),
        "=0": (series == 0).sum().item(),
    }
    stats["num_non_nulls"] = stats["count"] - stats["num_nulls"]
    if stats["num_non_nulls"] > 0:
        stats |= (
            series.dropna()
            .astype(float)
            .agg(
                {
                    "mean": "mean",
                    "median": "median",
                    "min": "min",
                    "max": "max",
                    "std": "std",
                    "q001": lambda x: x.quantile(0.001),
                    "q01": lambda x: x.quantile(0.01),
                    "q05": lambda x: x.quantile(0.05),
                    "q10": lambda x: x.quantile(0.1),
                    "q25": lambda x: x.quantile(0.25),
                    "q75": lambda x: x.quantile(0.75),
                    "q90": lambda x: x.quantile(0.9),
                    "q95": lambda x: x.quantile(0.95),
                    "q99": lambda x: x.quantile(0.99),
                    "q999": lambda x: x.quantile(0.999),
                }
            )
            .to_dict()
        )
        if stats["nunique"] > 1:
            array = data if isinstance(data, np.ndarray) else data.to_numpy(dtype=float)
            stats["skewness"] = float(skew(array, nan_policy="omit"))
            stats["kurtosis"] = float(kurtosis(array, nan_policy="omit"))
    return stats

from __future__ import annotations

__all__ = ["sort_by_keys"]


def sort_by_keys(mapping: dict) -> dict:
    r"""Sorts a dictionary by keys.

    Args:
        mapping (dict): Specifies the dictionary to sort.

    Returns:
        dict: The sorted dictionary.

    Example usage:

    .. code-block:: pycon

        >>> from flamme.utils.mapping import sort_by_keys
        >>> sort_by_keys({"dog": 1, "cat": 5, "fish": 2})
        {'cat': 5, 'dog': 1, 'fish': 2}
    """
    return dict(sorted(mapping.items()))

"""Utilitaires divers pour les calculs"""
from __future__ import annotations

from functools import reduce
from itertools import combinations
from typing import Any, Generator, List, Sequence, Tuple

import numpy as np

import mfire.utils.mfxarray as xr


def compute_RR_future(
    RR: xr.DataArray, n: int = 6, dim: str = "valid_time"
) -> xr.DataArray:
    """Returns the cumulative RR for the next n steps.

    Args:
        RR (xr.DataArray): The input DataArray containing precipitation values.
        n (int): The number of steps to compute the cumulative RR. Defaults to 6.
        dim (str): The dimension along which to compute the cumulative RR.
            Defaults to 'valid_time'.

    Returns:
        xr.DataArray: The cumulative RR for the next n steps.
    """
    nb_step = RR[dim].size

    # Compute the cumulative RR for the n preceding steps
    RR6_beg = (
        RR.rolling({dim: n}, min_periods=1)
        .sum()
        .shift({dim: -n + 1})
        .isel({dim: slice(None, nb_step - n + 1)})
    )

    # Compute the cumulative RR for the n following steps
    RR6_end = (
        RR.shift({dim: -n + 1})
        .rolling({dim: n}, min_periods=1)
        .sum()
        .isel({dim: slice(nb_step - n + 1, None)})
    )

    # Assign variable names
    RR6_beg.name = RR.name
    RR6_end.name = RR.name

    # Merge the two arrays and return the result
    result = xr.merge([RR6_beg, RR6_end])[RR.name]
    result.attrs["accum_hour"] = n
    return result


def round_to_closest_multiple(x: Any, m: Any) -> Any:
    """Return the multiple of m that is closest to x.

    Args:
        x (Any): The value to round.
        m (Any): The multiple to round to.

    Returns:
        Any: The multiple of m closest to x.
    """
    return m * np.round(x / m)


def round_to_next_multiple(x: Any, m: Any) -> Any:
    """Return the next multiple of m greater than or equal to x.

    Args:
        x (Any): The value to round.
        m (Any): The multiple to round to.

    Returns:
        Any: The next multiple of m greater than or equal to x.
    """
    return m * np.ceil(x / m)


def round_to_previous_multiple(x: Any, m: Any) -> Any:
    """Return the previous multiple of m less than or equal to x.

    Args:
        x (Any): The value to round.
        m (Any): The multiple to round to.

    Returns:
        Any: The previous multiple of m less than or equal to x.
    """
    return m * (x // m)


def combinations_and_remaining(
    objects: List, r: int
) -> Generator[Tuple[List, List], None, None]:
    """
    Generates all combinations and remaining elements of objects.
    The first element is the generated element of size r, and the second element is
    the remaining objects.
    Args:
        objects (List): The list of objects.
        r (int): The size of the generated combinations.
    Yields:
        Tuple[List, List]: A tuple containing the generated combination and the
            remaining objects.
    """
    for c in combinations(objects, r=r):
        diff = [i for i in objects if i not in c]
        yield list(c), diff


def all_combinations_and_remaining(
    objects: List, is_symmetric: bool = False
) -> Generator[Tuple[List, List], None, None]:
    """
    Generates all combinations and remaining objects of a list.
    If the `is_symmetric` argument is True, it only generates (combi, remaining) and
    not (remaining, combi), except for objects of even size and r=len(objects)/2.
    Args:
        objects (List): The list of objects.
        is_symmetric (bool): Indicates if symmetric combinations should be generated.
            Defaults to False.
    Yields:
        Tuple[List, List]: A tuple containing the generated combination and the
            remaining objects.
    """
    r_max = len(objects) // 2 if is_symmetric else len(objects)
    for r in range(r_max):
        yield from combinations_and_remaining(objects, r + 1)


def bin_to_int(sequence: Sequence[Any]) -> int:
    """Encode a given iterable containing binary values to an integer.

    For instances:
    >>> bin_to_int([1, 0, 1])
    5
    >>> bin_to_int("110")
    6

    Args:
        sequence: (Sequence): Sequence to encode

    Returns:
        int: encoded sequence
    """
    return reduce(lambda x, y: x * 2 + int(y), sequence, 0)


def all_close(a: Any, b: Any):
    def _all_close_func(i, j):
        if any((isinstance(i, str), isinstance(j, str), i is None, j is None)):
            return i == j
        return np.isclose(i, j)

    func = np.frompyfunc(_all_close_func, 2, 1)
    return np.all(func(a, b))

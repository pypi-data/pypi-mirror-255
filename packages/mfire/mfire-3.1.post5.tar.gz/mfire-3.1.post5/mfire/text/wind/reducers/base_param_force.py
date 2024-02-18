from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import numpy as np

import mfire.utils.mfxarray as xr


class BaseParamForce(ABC):
    """BaseParamForce class.

    Class used to store a gust or a wind force as an interval with a given precision
    (5 by default).
    """

    DEFAULT_PRECISION: int = 5
    PERCENTILE_NUM: int

    def __init__(self, force: float, precision: Optional[int] = None) -> None:
        self.precision: int = precision if precision else self.DEFAULT_PRECISION
        repr_value: int = self._get_repr_value(force)
        self._interval: tuple[int, int] = self._get_interval(repr_value)

    @property
    def repr_value(self) -> int:
        return self._interval[0]

    @property
    def interval(self) -> tuple[int, int]:
        return self._interval

    @classmethod
    def from_term_data_array(cls, data_array_wf: xr.DataArray) -> BaseParamForce:
        """Instantiate a BaseParamForce from a DataArray."""
        return cls(cls.data_array_to_value(data_array_wf))

    @classmethod
    @abstractmethod
    def data_array_to_value(cls, data_array: xr.DataArray) -> float:
        """Find the value which represents the input DataArray."""

    def _get_repr_value(self, force: float) -> int:
        """Get the representative value of the given force."""
        return int((np.floor(force) // self.DEFAULT_PRECISION) * self.DEFAULT_PRECISION)

    def _get_interval(self, repr_value) -> tuple[int, int]:
        """Get the force interval from the given representative value."""
        upper_bound: int = repr_value + self.precision
        return repr_value, upper_bound

    def __eq__(self, other: BaseParamForce) -> bool:
        return self.repr_value == other.repr_value

    def __le__(self, other: BaseParamForce) -> bool:
        return self.repr_value <= other.repr_value

    def __lt__(self, other: BaseParamForce) -> bool:
        return self.repr_value < other.repr_value

    def __ge__(self, other: BaseParamForce) -> bool:
        return self.repr_value >= other.repr_value

    def __gt__(self, other: BaseParamForce) -> bool:
        return self.repr_value > other.repr_value

    def __hash__(self) -> int:
        return hash(self.repr_value)

    def __repr__(self):
        return f"{self.__class__.__name__}(interval=[{self._interval}])"

from __future__ import annotations

import copy
import numpy as np
import xarray as xr
from typing import Optional

from mfire.settings import get_logger
from mfire.text.wind.reducers.wind_summary_builder.helpers import (
    BaseWindPeriod,
    BaseWindPeriodFinder,
    PandasWindSummary,
    WindPeriodsInitializer,
)
from mfire.utils.date import Datetime, Timedelta

from .sympo_code_direction import SympoCodeDirection

# Logging
LOGGER = get_logger(name="wind_direction.mod", bind="wind_direction")


class WindDirection:
    """WindDirection class."""

    SYMPO_INTERVAL_SIZE: float = 22.5

    def __init__(self, degrees: list[float]):
        self._lower_bound: float = 0
        self._upper_bound: float = 0
        self._size: float = 0
        self._sympo_code: int = 0
        self._initialize(degrees)

    @staticmethod
    def _check_degrees(degrees: list[float]):
        if 0.0 in degrees:
            raise ValueError(
                "0.0 found in input degrees when creating an instance of WindDirection"
            )

    def _initialize(self, degrees: list[float]):
        """Initialize WindDirection attributes from list of degrees."""
        self._check_degrees(degrees)
        self._lower_bound = min(degrees)
        self._upper_bound = max(degrees)

        if self._upper_bound - self._lower_bound <= 180.0:
            self._size = self._upper_bound - self._lower_bound
            self._sympo_code: int = self.to_sympo_code()
            return

        for idx, deg in enumerate(degrees):
            if (deg - self._lower_bound) > 180.0:
                degrees[idx] = -(360.0 - deg)

        self._lower_bound = min(degrees)
        self._upper_bound = max(degrees)

        # Compute interval size
        self._size = (self._upper_bound - self._lower_bound) % 360

        # Update bounds if necessary
        if self._upper_bound == 0.0:
            self._upper_bound = 360.0

        if self._lower_bound == 0.0:
            self._lower_bound = self._upper_bound
            self._upper_bound = 360.0

        self._sympo_code: int = self.to_sympo_code()

    @property
    def size(self):
        return self._size

    @property
    def lower_bound(self):
        return self._lower_bound

    @property
    def upper_bound(self):
        return self._upper_bound

    def check_size(self, size_max: float) -> bool:
        return self._size <= size_max

    @property
    def middle(self) -> float:
        upper_bound = (
            self._lower_bound if self._upper_bound == 360.0 else self.upper_bound
        )
        return (upper_bound - self._size / 2) % 360

    @property
    def sympo_code(self) -> int:
        return self._sympo_code

    def to_sympo_code(self) -> int:
        """Get the sympo code of the WindDirection."""
        tmp = self.middle / self.SYMPO_INTERVAL_SIZE
        return int(round(tmp, 0)) % 16

    def is_opposite_to(self, other: WindDirection) -> bool:
        """Check if the WindDirection is the opposite of another WindDirection.

        For this check, the sympo code is used. For example, WindDirections with sympo
        code 0 and 8 are opposite but WindDirections with sympo code 0 and 7 are not.
        """
        return (self.sympo_code - other.sympo_code) % 8 == 0

    def __add__(self, other: WindDirection) -> WindDirection:
        """Add 2 WindDirection."""
        return WindDirection(
            [
                self.lower_bound,
                self.upper_bound,
                other.lower_bound,
                other.upper_bound,
            ]
        )

    def __hash__(self):
        return hash(self.sympo_code)

    def __eq__(self, other: Optional[WindDirection]):
        return isinstance(other, WindDirection) and self.sympo_code == other.sympo_code

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(interval=[{self._lower_bound}, "
            f"{self._upper_bound}], size={self._size}, sympo_code={self.sympo_code})"
        )


class WindDirectionPeriod(BaseWindPeriod[WindDirection]):
    """WindDirectionPeriod class."""

    @property
    def sympo_code(self) -> int:
        return self._wind_element.sympo_code

    @property
    def direction(self) -> str:
        return SympoCodeDirection.get_direction_from_sympo_code(self.sympo_code)

    def update(
        self,
        other: WindDirectionPeriod,
        **kwargs,
    ) -> bool:
        """Try to update the current WindDirectionPeriod.

        If the size of the resulting WindDirection is <= size_max, then it returns
        True, else False.
        """
        if super().update(other, **kwargs) is False:
            return False

        # Get size_max key argument
        size_max: float = kwargs["size_max"]

        # Get WindDirection
        wind_direction: WindDirection = self.wind_element + other.wind_element

        if wind_direction.check_size(size_max):
            self._period.end_time = other.end_time
            self._wind_element = wind_direction
            return True
        return False

    def has_same_direction_than(self, other: WindDirectionPeriod) -> bool:
        """Check if 2 WindDirectionPeriod has the same direction."""
        return self.wind_element == other.wind_element

    def has_opposite_direction_to(self, other: WindDirectionPeriod) -> bool:
        """Check if 2 WindDirectionPeriod has opposite directions."""
        return self.wind_element.is_opposite_to(other.wind_element)

    def __repr__(self):
        s = (
            f"{self.__class__.__name__}(begin_time={self.begin_time}, "
            f"end_time={self.end_time}, duration={self.duration}, "
            f"wind_direction={self._wind_element}, sympo_code={self.sympo_code}, "
            f"direction='{self.direction}')"
        )
        return s

    def summarize(self, reference_datetime: Datetime) -> dict:
        """Summarize the WindDirectionPeriod."""
        summary: dict = super().summarize(reference_datetime)
        summary[self.WD] = self.direction

        return summary


class WindDirectionPeriodsInitializer(WindPeriodsInitializer[WindDirection]):

    DEGREES_SECTOR_SIZE: float = 22.5
    PERCENT_MIN: float = 100.0
    TERM_DIRECTION_SIZE_MAX: float = 4 * DEGREES_SECTOR_SIZE

    @classmethod
    def _get_unique_values_of_wd_array(cls, wd_array: np.ndarray) -> list:
        """Get all unique values of a wind direction array."""
        unique, count = np.unique(wd_array, return_counts=True)
        unique_counts = list(zip(unique, count))
        unique_counts.sort(key=lambda e: e[1], reverse=True)
        return unique_counts

    @classmethod
    def _get_most_populated_wind_directions_of_wd_ndarray(
        cls, wd_array: np.ndarray
    ) -> Optional[WindDirection]:
        """Get the most populated wind direction of an array."""
        not_nan_count: int = np.count_nonzero(~np.isnan(wd_array))
        unique_counts: list = cls._get_unique_values_of_wd_array(wd_array)

        met_values: list = []
        met_points_counter: int = 0

        for value, count in unique_counts:

            if np.isnan(value):
                continue

            met_points_counter += count
            met_values.append(value)
            percent = met_points_counter * 100.0 / not_nan_count

            if percent >= cls.PERCENT_MIN:
                return WindDirection(met_values)

        return None

    @classmethod
    def _get_term_period(
        cls,
        term_data: xr.DataArray,
        pd_summary: PandasWindSummary,
    ) -> Optional[WindDirectionPeriod]:
        """Compute the WindDirectionPeriod of the input term data."""

        wd = cls._get_most_populated_wind_directions_of_wd_ndarray(term_data.values)

        if wd is None:
            return None

        valid_time: np.datetime64 = term_data.valid_time.values

        # Keep wind direction if its check is OK
        if wd.check_size(cls.TERM_DIRECTION_SIZE_MAX):
            return WindDirectionPeriod(
                pd_summary.get_term_previous_time(valid_time), Datetime(valid_time), wd
            )

        return None

    @classmethod
    def _create_wind_direction_instance(
        cls, degrees: list[float]
    ) -> Optional[WindDirection]:
        """Create a WindDirection from a degrees list."""
        wind_direction = WindDirection(copy.deepcopy(degrees))
        check: bool = wind_direction.check_size(cls.TERM_DIRECTION_SIZE_MAX)
        return wind_direction if check else None

    @classmethod
    def _check_term_period(
        cls,
        term_period: WindDirectionPeriod,
    ) -> bool:
        """Check term_period"""
        return term_period is not None


class WindDirectionPeriodFinder(BaseWindPeriodFinder[WindDirection]):

    TERM_DIRECTION_SIZE_MAX: float = (
        4 * WindDirectionPeriodsInitializer.DEGREES_SECTOR_SIZE
    )
    MULTIPLE_TERMS_DIRECTION_SIZE_MAX: float = (
        6 * WindDirectionPeriodsInitializer.DEGREES_SECTOR_SIZE
    )
    PERIOD_DURATION_MIN: Timedelta = Timedelta(hours=3)
    WIND_PERIOD_INITIALIZER = WindDirectionPeriodsInitializer

    def check_terms(self) -> bool:
        """Check all data terms."""
        return False if not self._initial_periods else True

    def _update_period(
        self, period1: WindDirectionPeriod, period2: WindDirectionPeriod
    ) -> Optional[WindDirectionPeriod]:
        update_res: bool = period1.update(
            period2, size_max=self.MULTIPLE_TERMS_DIRECTION_SIZE_MAX
        )
        if update_res:
            return period1
        return None

    def _find_periods(self) -> list[BaseWindPeriod[WindDirection]]:
        """Find all wind direction periods as a list.

        If a term has no wind direction, then the result is an empty list.
        """
        periods: list[BaseWindPeriod[WindDirection]]

        if self.check_terms() is False:
            periods = []
        else:
            periods = super()._find_periods()

        return periods

    def _check_terms_coverage(self, periods_list) -> bool:
        """Check if the times of the 1st and the last member of initial_periods and
        periods_list match.

        It checks if:
        - the first period start at the beginning of initial_periods[0]
        - the last period ends et the end of initial_periods[-1]
        """
        if not periods_list:
            return False

        return (
            periods_list[0].begin_time == self._initial_periods[0].begin_time
            and periods_list[-1].end_time == self._initial_periods[-1].end_time
        )

    def post_process_found_periods(
        self, periods: list[WindDirectionPeriod]
    ) -> list[WindDirectionPeriod]:
        """Post process found periods."""

        # Keep only periods with at have at least a 3 hours duration
        f_periods: list[WindDirectionPeriod] = [
            period for period in periods if period.duration >= self.PERIOD_DURATION_MIN
        ]

        # If the 1st and the last period
        if self._check_terms_coverage(f_periods) is False:
            return []

        # If there is more than 1 WindDirectionPeriod periods, keep only the 1st and
        # the last
        if len(f_periods) > 1:
            # If the 1st and tge last direction are the same, then don't keep these
            if f_periods[0].wind_element == f_periods[-1].wind_element:
                period: Optional[WindDirectionPeriod] = self._update_period(
                    f_periods[0], f_periods[-1]
                )
                f_periods = [period] if period else []

            # If they are opposite, then don't keep these too
            elif f_periods[0].wind_element.is_opposite_to(f_periods[-1].wind_element):
                f_periods = []

            # Else keep the 1st and the last period
            else:
                f_periods = [f_periods[0], f_periods[-1]]

        return f_periods

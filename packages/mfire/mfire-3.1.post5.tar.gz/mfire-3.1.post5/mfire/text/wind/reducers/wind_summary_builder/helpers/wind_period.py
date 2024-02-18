from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

import numpy as np
import pandas as pd

import mfire.utils.mfxarray as xr
from mfire.settings import get_logger
from mfire.text.wind.reducers.wind_summary_builder.helpers import (
    PandasWindSummary,
    SummaryKeysMixin,
)
from mfire.utils.date import Datetime, Period, Timedelta

# Logging
LOGGER = get_logger(name="wind_period.mod", bind="wind_period")

WindElement = TypeVar("WindElement")


class WindPeriodMixin:
    def __init__(
        self,
        begin_time: Datetime,
        end_time: Datetime,
    ):
        if begin_time > end_time:
            raise ValueError(f"begin_time '{begin_time}' > end_time '{end_time}'")
        self._period: Period = Period(begin_time, end_time)

    @property
    def begin_time(self) -> Datetime:
        """begin_time

        Returns:
            Datetime: Beginning of the period
        """
        return self._period.begin_time

    @property
    def end_time(self) -> Datetime:
        """end_time

        Returns:
            Datetime: End of the period
        """
        return self._period.end_time

    @property
    def period(self) -> Period:
        return self._period

    @property
    def duration(self) -> Timedelta:
        return self._period.duration


class BaseWindPeriod(SummaryKeysMixin, WindPeriodMixin, ABC, Generic[WindElement]):
    """BaseWindPeriod abstract class."""

    DURATION_LOWER_BOUND: Timedelta = Timedelta(hours=1)

    def __init__(
        self,
        begin_time: Datetime,
        end_time: Datetime,
        wind_element: WindElement,
    ):
        # Check begin and end times
        if begin_time >= end_time or end_time < begin_time + self.DURATION_LOWER_BOUND:
            raise ValueError(
                f"end_time has to be >= begin_time + 1h and this is not the case:"
                f"begin_time: '{begin_time}', end_time: '{end_time}' !"
            )

        self._period: Period = Period(begin_time, end_time)
        super().__init__(begin_time, end_time)
        self._wind_element: WindElement = wind_element

    @property
    def wind_element(self) -> WindElement:
        return self._wind_element

    @wind_element.setter
    def wind_element(self, wind_element: WindElement) -> None:
        self._wind_element = wind_element

    def __eq__(self, other: Optional[BaseWindPeriod[WindElement]]) -> bool:
        if other is None:
            return False
        return self.period == other.period and self.wind_element == other.wind_element

    def __add__(self, other: BaseWindPeriod) -> BaseWindPeriod:
        """Add 2 WindPeriod instances."""
        # Get the WindPeriod with the maximum end_time
        p_max: BaseWindPeriod = max(self, other, key=lambda b: b.end_time)

        return self.__class__(
            min(self.begin_time, other.begin_time),
            p_max.end_time,
            self.wind_element + other.wind_element,
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.period,
                self.wind_element,
            )
        )

    def update(self, other: BaseWindPeriod, **kwargs):
        """Try to update the period with another period."""
        if self.end_time > other.begin_time:
            LOGGER.warning(
                f"Try to update a {self.__class__.__name__} with another which has a "
                f"too early begin_time: {self.end_time} > {other.begin_time} !"
            )
            return False

        return True

    def summarize(self, reference_datetime: Datetime) -> dict:
        """Summarize the WindPeriod instance."""
        return {
            self.BEGIN_TIME_MARKER: self.begin_time.describe_as_period(
                reference_datetime
            ),
            self.END_TIME_MARKER: self.end_time.describe_as_period(reference_datetime),
            self.TIME_DESC: self.period.describe(reference_datetime),
        }


class WindPeriodsInitializer(ABC, Generic[WindElement]):
    @classmethod
    def get_term_periods(
        cls,
        data_array: xr.DataArray,
        pd_summary: PandasWindSummary,
        valid_times: np.ndarray | pd.Index,
    ) -> list[BaseWindPeriod[WindElement]]:
        """Compute the period of terms with valid_times contained in data_array."""
        term_periods: list[BaseWindPeriod[WindElement]] = []

        for valid_time in valid_times:

            term_data: xr.DataArray = data_array.sel(valid_time=valid_time)

            # Get term period
            term_period: Optional[BaseWindPeriod] = cls._get_term_period(
                term_data, pd_summary
            )

            if cls._check_term_period(term_period) is False:
                return []

            if term_period is not None:
                term_periods.append(term_period)

        return term_periods

    @classmethod
    @abstractmethod
    def _get_term_period(
        cls,
        term_data: xr.DataArray,
        pd_summary: PandasWindSummary,
    ) -> Optional[BaseWindPeriod[WindElement]]:
        """Compute the period of the given term."""
        pass

    @classmethod
    def _check_term_period(
        cls,
        term_period: Optional[BaseWindPeriod[WindElement]],
    ) -> bool:
        """Check term_period."""
        return True


class BaseWindPeriodFinder(ABC, Generic[WindElement]):
    """BaseWindPeriodFinder class."""

    WIND_PERIOD_INITIALIZER: WindPeriodsInitializer = WindPeriodsInitializer

    def __init__(
        self,
        initial_periods: list[BaseWindPeriod[WindElement]],
    ):
        """Initialize a BaseWindPeriodFinder instance.

        _initial_periods is a list of BaseWindPeriod. _find_periods uses it to find
        long enough periods. Short member will not be kept.
        This attribute is protected and its contain never changes during the finding
        process performed by the public method run.
        """
        self._initial_periods: list[BaseWindPeriod[WindElement]] = initial_periods
        self._ind_max: int = len(self._initial_periods) - 1
        self._ind: int = 0

    @classmethod
    def from_data_array(
        cls,
        data_array: xr.DataArray,
        pd_summary: PandasWindSummary,
        valid_times: np.ndarray | pd.Index,
    ) -> BaseWindPeriodFinder:
        """Initialize a period finder from its term-periods."""
        periods: list[BaseWindPeriod[WindElement]]
        periods = cls.WIND_PERIOD_INITIALIZER.get_term_periods(
            data_array, pd_summary, valid_times
        )
        return cls(periods)

    @property
    def initial_periods(self) -> list[WindElement]:
        """Get the periods list."""
        return self._initial_periods

    @abstractmethod
    def _update_period(
        self, period1: BaseWindPeriod, period2: BaseWindPeriod
    ) -> Optional[BaseWindPeriod[WindElement]]:
        pass

    def _find_periods(self) -> list[BaseWindPeriod[WindElement]]:
        """Find all wind periods as a list."""

        # Initialize the index
        self._ind = 0

        period_prev: Optional[BaseWindPeriod[WindElement]] = None
        periods = []

        while self._ind <= self._ind_max:

            period_cur: Optional[BaseWindPeriod[WindElement]]
            period_cur = self._initial_periods[self._ind]

            if period_prev is None:
                period_prev = period_cur
            elif period_cur is None:
                periods.append(period_prev)
                period_prev = None
            else:
                period_updated: Optional[
                    BaseWindPeriod[WindElement]
                ] = self._update_period(period_prev, period_cur)

                # If the update succeeded, then continue
                if period_updated is None:
                    periods.append(period_prev)
                    period_prev = period_cur

            self._ind += 1

        if period_prev is not None:
            periods.append(period_prev)

        return periods

    def post_process_found_periods(
        self, periods_list: list[BaseWindPeriod[WindElement]]
    ) -> list[BaseWindPeriod[WindElement]]:
        """Post process found periods."""
        return periods_list

    def run(self) -> list[BaseWindPeriod[WindElement]]:
        """Run the period finder."""
        periods: list[BaseWindPeriod[WindElement]] = self._find_periods()

        if periods:
            periods = self.post_process_found_periods(periods)

        return periods

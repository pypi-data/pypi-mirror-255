from __future__ import annotations

import numpy as np
from typing import Optional

import mfire.utils.mfxarray as xr
from mfire.settings import get_logger
from mfire.text.wind.reducers.base_param_force import BaseParamForce
from mfire.text.wind.reducers.wind_summary_builder.helpers import (
    BaseWindPeriod,
    BaseWindPeriodFinder,
    PandasWindSummary,
    WindPeriodsInitializer,
)
from mfire.utils.date import Datetime, Period

# Logging
LOGGER = get_logger(name="wind_force.mod", bind="wind_force")


class WindForce(BaseParamForce):
    """WindForce class."""

    DEFAULT_PRECISION: int = 5
    PERCENTILE_NUM: int = 95

    def __init__(self, force: float, precision: int = DEFAULT_PRECISION):
        super().__init__(force, precision)

    def __add__(self, other: WindForce) -> WindForce:
        """Add 2 WindForce instances."""
        lower_bound: int = min(self.interval[0], other.interval[0])
        upper_bound: int = max(self.interval[1], other.interval[1])
        precision: int = upper_bound - lower_bound

        return WindForce(lower_bound, precision)

    @classmethod
    def data_array_to_value(cls, data_array: xr.DataArray) -> float:
        """Find the value which represents the input DataArray."""
        return float(np.nanpercentile(data_array.values, cls.PERCENTILE_NUM))


class WindForcePeriod(BaseWindPeriod[WindForce]):
    """WindForcePeriod class."""

    def update(self, other: WindForcePeriod, **kwargs) -> bool:
        """Update the period with a Datetime and a WindForce."""
        if super().update(other, **kwargs) is False:
            return False

        if self.wind_element != other._wind_element:
            return False

        self._period.end_time = other.end_time
        return True

    @property
    def period(self) -> Period:
        return self._period

    def has_same_force_than(self, other: WindForcePeriod) -> bool:
        return self.wind_element == other.wind_element

    def is_juxtaposed_with(self, other: WindForcePeriod):
        wf1: WindForce = self.wind_element
        wf2: WindForce = other.wind_element
        precision: int = WindForce.DEFAULT_PRECISION

        if (wf1.precision, wf2.precision) != (precision, precision):
            return False

        if wf1.repr_value == wf2.repr_value + precision:
            return True
        if wf2.repr_value == wf1.repr_value + precision:
            return True
        return False

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(begin_time={self.begin_time}, "
            f"end_time={self.end_time}), wind_force={self.wind_element}"
        )

    def summarize(self, reference_datetime: Datetime) -> dict:
        """Summarize the WindForcePeriod instance."""
        summary: dict = super().summarize(reference_datetime)
        summary[self.WF_INTERVAL] = self.wind_element.interval

        return summary


class WindForcePeriodsInitializer(WindPeriodsInitializer[WindForce]):
    @classmethod
    def _get_term_period(
        cls,
        term_data: xr.DataArray,
        pd_summary: PandasWindSummary,
    ) -> Optional[WindForcePeriod]:
        """Compute the WindForcePeriod of the input term data."""

        wind_force: WindForce = WindForce.from_term_data_array(term_data)

        valid_time: np.datetime64 = term_data.valid_time.values

        return WindForcePeriod(
            pd_summary.get_term_previous_time(valid_time),
            Datetime(valid_time),
            wind_force,
        )

    @classmethod
    def _check_term_period(
        cls,
        term_period: Optional[WindForcePeriod],
    ) -> bool:
        """Check term_period."""
        if term_period is None:
            raise ValueError(
                "A term with a None WindForcePeriod found by a"
                " WindForcePeriodsInitializer instance !"
            )
        return True


class WindForcePeriodFinder(BaseWindPeriodFinder[WindForce]):

    WIND_PERIOD_INITIALIZER = WindForcePeriodsInitializer

    def _update_period(
        self, period1: WindForcePeriod, period2: WindForcePeriod
    ) -> Optional[WindForcePeriod]:
        update_res: bool = period1.update(period2)
        if update_res:
            return period1
        return None

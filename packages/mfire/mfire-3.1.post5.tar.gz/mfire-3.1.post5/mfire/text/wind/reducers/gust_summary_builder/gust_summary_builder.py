import copy
import traceback
from typing import Optional

import numpy as np

import mfire.utils.mfxarray as xr
from mfire.composite import WeatherComposite
from mfire.settings import get_logger
from mfire.text.wind.exceptions import WindSynthesisError
from mfire.text.wind.reducers.base_param_force import BaseParamForce
from mfire.text.wind.reducers.base_param_summary_builder import BaseParamSummaryBuilder
from mfire.text.wind.reducers.gust_summary_builder.mixins import GustSummaryBuilderMixin
from mfire.text.wind.reducers.utils import initialize_previous_time
from mfire.utils.date import Datetime, Period, Timedelta

from .gust_enum import GustCase

# Logging
LOGGER = get_logger(name="gust_summary_builder.mod", bind="gust_summary_builder")


class GustForce(BaseParamForce):
    """GustForce class."""

    DEFAULT_PRECISION: int = 10
    PERCENTILE_NUM: int = 90

    @classmethod
    def data_array_to_value(cls, data_array: xr.DataArray) -> float:
        """Find the value which represents the input DataArray."""
        return round(np.nanpercentile(data_array.values, cls.PERCENTILE_NUM), 2)


class GustSummaryBuilder(GustSummaryBuilderMixin, BaseParamSummaryBuilder):

    FORCE_MIN: int = 50
    GUST: str = "gust"
    PERIODS_SEPARATION_TIME: Timedelta = Timedelta(hours=3)
    PERIODS_MIN_TIME: Timedelta = Timedelta(hours=3)
    CACHED_EXCEPTIONS: tuple[Exception] = (WindSynthesisError,)
    ALONG_ALL_THE_PERIOD: str = "durant toute la période"
    INTERMITTENTLY: str = "par intermittence"
    PUNCTUALLY: str = "ponctuellement"
    AS_WELL_AS: str = " ainsi que "

    def __init__(self, compo: WeatherComposite, data_array: xr.DataArray):
        # Call SummaryBuilderMixin.__init__ and create the summary attribute
        super().__init__()

        self.units: str = self._get_composite_units(compo, self.GUST)

        # Get gust data: nan values will be kept
        self.data: xr.DataArray = self._get_data_array(
            data_array, self.GUST, units=self.units
        )

        self._monitoring_period: Period = Period(
            Datetime(initialize_previous_time(self.data.valid_time.values)),
            Datetime(self.data.valid_time.values[-1]),
        )

    def _get_initial_gust_periods(self) -> list[Period]:
        previous_time: Datetime = self._monitoring_period.begin_time
        initial_periods: list[Period] = []
        period_cur: Optional[Period] = None

        for valid_time in self.data.valid_time.values:
            term_data: np.ndarray = self.data.sel(valid_time=valid_time).values
            term_da = np.where(term_data > self.FORCE_MIN)

            if np.isnan(term_da).all():
                if period_cur is not None:
                    initial_periods.append(period_cur)
                period_cur = None

            else:
                if period_cur is None:
                    period_cur = Period(previous_time)
                period_cur.end_time = valid_time

            previous_time = valid_time

        if period_cur is not None:
            initial_periods.append(period_cur)

        # If gust found, then try to merge gust periods
        if self.case_value != GustCase.CASE_1.value:
            if len(initial_periods) == 0:
                raise WindSynthesisError(
                    "No gust period found before merging step while there is gust !"
                )

        return initial_periods

    def _merge_gust_periods(self, initial_periods: list[Period]):
        merged_periods: list[Period] = copy.deepcopy(initial_periods)
        i: int = 0
        bound: int = len(merged_periods)

        while i < bound - 1:
            period_cur: Period = merged_periods[i]

            time_diff: Timedelta
            time_diff = merged_periods[i + 1].begin_time - period_cur.end_time
            if time_diff <= self.PERIODS_SEPARATION_TIME:
                period_cur.end_time = merged_periods[i + 1].end_time
                merged_periods[i] = period_cur
                merged_periods.pop(i + 1)
                bound -= 1
            else:
                i += 1

        # Keep only periods >= 3h
        i = 0
        while i < bound:
            if merged_periods[i].duration < self.PERIODS_MIN_TIME:
                merged_periods.pop(i)
                bound -= 1
                continue
            i += 1

        return merged_periods

    def __period_match_monitoring_period(self, period: Period) -> bool:
        return self._monitoring_period == period

    def __describe_period(
        self,
        period_merged: Period,
        reference_datetime: Optional[Datetime] = None,
        prefix: Optional[str] = None,
    ) -> Optional[str]:
        res: Optional[str] = None

        if self.__period_match_monitoring_period(period_merged):
            res = self.ALONG_ALL_THE_PERIOD
        elif reference_datetime is not None:
            res = f"{period_merged.describe(reference_datetime)}"

        if res is None:
            return prefix if prefix else None

        return f"{prefix} {res}" if prefix else res

    def __describe_period_intermittently(
        self, period_merged: Period, reference_datetime: Datetime
    ) -> str:
        return self.__describe_period(
            period_merged, reference_datetime, self.INTERMITTENTLY
        )

    def _describe_gust_temporalities(
        self,
        periods_merged: list[Period],
        reference_datetime: Datetime,
    ) -> tuple[Optional[str], Optional[str]]:
        """Return the description of the periods_merged with a facultative prefix.

        If periods_merged is empty, then its description is None.
        """
        periods_merged_cnt: int = len(periods_merged)

        if periods_merged_cnt == 0:
            return self.PUNCTUALLY, None

        if periods_merged_cnt >= 3:
            return None, self.__describe_period_intermittently(
                Period(periods_merged[0].begin_time, periods_merged[-1].end_time),
                reference_datetime,
            )

        if periods_merged_cnt == 1:
            return None, self.__describe_period(periods_merged[0], reference_datetime)

        # Else which means periods_merged_cnt == 2
        return None, self.AS_WELL_AS.join(
            [period.describe(reference_datetime) for period in periods_merged]
        )

    def _generate_summary(self, reference_datetime: Datetime) -> None:
        """Compute the gust summary."""
        case: GustCase

        # Get the maximum gust value for each point for the all period
        data_array: xr.DataArray = self.data.max(dim="valid_time")

        # Keep only the values > FORCE_MIN
        data_array = data_array.where(data_array > self.FORCE_MIN)

        # If all gust are nan or <= FORCE_MIN, then case is case 1
        if np.isnan(data_array).all():
            self._set_summary_case(GustCase.CASE_1)
        # Else, we get the gust force interval
        else:
            gust_force: GustForce = GustForce.from_term_data_array(data_array)

            periods_init: list[Period] = self._get_initial_gust_periods()
            periods_merged = self._merge_gust_periods(periods_init)

            gust_temporalities: tuple[Optional[str], Optional[str]]
            gust_temporalities = self._describe_gust_temporalities(
                periods_merged, reference_datetime
            )

            self._summary.update(
                {
                    "units": self.units,
                    "gust_interval": gust_force.interval,
                    "gust_tempos": gust_temporalities,
                    "force_min": self.FORCE_MIN,
                }
            )
            self._set_summary_case(GustCase.CASE_2)

    def compute(self, reference_datetime: Datetime) -> dict:
        """Compute the gust summary."""
        try:
            self._generate_summary(reference_datetime)
        except self.CACHED_EXCEPTIONS as exp:
            msg: str = (
                f"{exp.__class__.__name__}: problem detected in GustSummaryBuilder -> "
                f"{traceback.format_exc()}"
            )

            self._add_error_case_in_summary(self._summary, msg)

        return {self.GUST: self._summary}

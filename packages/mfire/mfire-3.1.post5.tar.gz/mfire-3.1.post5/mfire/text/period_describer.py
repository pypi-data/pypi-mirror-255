"""
@package text.period

Module for describing textually periods
"""

# Built-in packages
from __future__ import annotations

from typing import Optional, Union

# Own package
from mfire.settings import TEMPLATES_FILENAMES, Settings, get_logger
from mfire.utils.date import Datetime, Period, Periods
from mfire.utils.json_utils import JsonFile
from mfire.utils.string_utils import concatenate_string

# Logging
LOGGER = get_logger(name="text.period.mod", bind="text.period")

DATES = JsonFile(TEMPLATES_FILENAMES[Settings().language]["date"]).load()


class PeriodDescriber:
    """PeriodDescriber: Class for describing periods or sequences of periods.
    If a single period is given, the class will simply use the period.describe
    method.
    Else, if a sequence of periods is given, the period describer will first
    try to reduce the number of periods by merging those which extends themselves,
    and then will use the period.describe method on all the reduced periods.

    Args:
        request_time (Datetime): Point of view used for describing the
            given periods
    """

    def __init__(self, request_time: Datetime) -> None:
        self.request_time = Datetime(request_time)

    def reduce(self, periods: Periods, n: Optional[int] = None) -> Periods:
        """reduce: method which reduces a sequence of periods to another sequence
        of periods, where those new periods are a merging of previous periods that
        extends themselves.

        Args:
            periods (Periods): Sequence of periods to reduce.
            n (Optional[int]): number of periods that we want to keep

        Returns:
            Periods: Reduced periods.
        """
        new_periods = Periods()
        if len(periods) == 0:
            return new_periods

        current_period = periods.pop(0)
        for period in periods:
            if period.extends(current_period, request_time=self.request_time):
                current_period = current_period.basic_union(period)
            else:
                new_periods += [current_period]
                current_period = period
        new_periods += [current_period]
        return new_periods.reduce(n)

    def describe_multi(self, periods: Periods, to_reduce: bool = True) -> str:
        """describe_multi: takes a sequence of periods and returns
        a textual description of this sequence of periods.

        Args:
            periods (Periods): Sequence of periods to describe.

        Returns:
            str: textual description of the given sequence.
        """
        if to_reduce:
            periods = self.reduce(periods)
        if len(periods) == 1:
            return periods[0].describe(self.request_time)
        return concatenate_string((p.describe(self.request_time) for p in periods))

    def describe(self, periods: Union[Periods, Period], to_reduce: bool = True) -> str:
        """describe: method for describing periods or sequences of periods.
        If a single period is given, the method will simply use the period.describe
        method.
        Else, if a sequence of periods is given, the period describer will first
        try to reduce the number of periods by merging those which extends themselves,
        and then will use the period.describe method on all the reduced periods.

        Args:
            periods (Union[Periods, Period]): Periods to describe.

        Returns:
            str: Textual description of given period(s)
        """
        if isinstance(periods, Period):
            return periods.describe(self.request_time)
        return self.describe_multi(periods, to_reduce)

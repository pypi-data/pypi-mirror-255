from __future__ import annotations

import copy
from functools import reduce
from typing import Optional

from mfire.settings import get_logger
from mfire.text.wind.exceptions import WindSynthesisError
from mfire.text.wind.reducers.wind_summary_builder.helpers import (
    SummaryKeysMixin,
    SummaryValuesMixin,
    WindCase,
    WindSummaryBuilderMixin,
)
from mfire.text.wind.reducers.wind_summary_builder.wind_direction import (
    WindDirectionPeriod,
)
from mfire.text.wind.reducers.wind_summary_builder.wind_force import (
    WindForce,
    WindForcePeriod,
)
from mfire.utils.date import Datetime

from .wind_block import WindBlock

LOGGER = get_logger(
    name="one_type3_blocks_summary_builder.mod", bind="one_type3_blocks_summary_builder"
)


class OneType3BlockSummaryBuilder(
    WindSummaryBuilderMixin, SummaryKeysMixin, SummaryValuesMixin
):
    """OneType3BlockSummaryBuilder class."""

    def __init__(self, block: WindBlock):
        super().__init__()
        self.case: Optional[WindCase] = None
        self.block: WindBlock = copy.deepcopy(block)

        self._preprocess()

    def _get_wind_force_variation_marker(self, wf1: WindForce, wf2: WindForce) -> str:
        """Get the word which describe the evolution of 2 Wind Forces."""
        if wf1.repr_value == wf2.repr_value:
            raise WindSynthesisError(f"wf1 '{wf1}' = wf2 '{wf2}'")
        if wf1.repr_value < wf2.repr_value:
            return self.GROWING_MARKER
        return self.DECREASING_MARKER

    @staticmethod
    def _direction_period_match_force_period(
        dir_period: WindDirectionPeriod, force_period: WindForcePeriod
    ) -> bool:
        """Check if a direction periods and a force periods have the same dates."""
        if dir_period.begin_time != force_period.begin_time:
            return False
        if dir_period.end_time != force_period.end_time:
            return False
        return True

    def _direction_periods_match_force_periods(
        self,
        dir_periods: list[WindDirectionPeriod],
        force_periods: list[WindForcePeriod],
    ) -> bool:
        """Check if direction periods and force periods have the same dates."""
        for dir_period, force_period in zip(dir_periods, force_periods):
            if not self._direction_period_match_force_period(dir_period, force_period):
                return False
        return True

    def _1_wind_force_period_process(self) -> WindCase:
        """Deal when there is 1 WindForcePeriod."""
        wd_period_cnt: int = len(self.block.wd_periods)

        if wd_period_cnt == 0:
            return WindCase.CASE_3_1B_3
        if wd_period_cnt == 1:
            return WindCase.CASE_3_1B_1
        return WindCase.CASE_3_1B_2  # ie there are 2 wd periods

    def _2_wind_force_periods_process(self) -> WindCase:
        """Deal when there are 2 WindForcePeriods."""
        wd_period_cnt: int = len(self.block.wd_periods)

        # if wind forces are juxtaposed
        if self.block.wf_periods[0].is_juxtaposed_with(self.block.wf_periods[1]):
            self._concatenate_wf_periods()
            if wd_period_cnt == 0:
                return WindCase.CASE_3_1B_10
            if wd_period_cnt == 1:
                return WindCase.CASE_3_1B_5
            return WindCase.CASE_3_1B_8  # ie there are 2 wd periods

        # else if wind forces are not juxtaposed
        if wd_period_cnt == 0:
            return WindCase.CASE_3_1B_9
        if wd_period_cnt == 1:
            return WindCase.CASE_3_1B_4

        # Else it means than there are 2 wd periods
        # if changes are simultaneous
        if (
            self._direction_periods_match_force_periods(
                self.block.wd_periods, self.block.wf_periods
            )
            is True
        ):
            return WindCase.CASE_3_1B_7
        # if changes are not simultaneous
        return WindCase.CASE_3_1B_6

    def _more_than_3_wind_force_periods_process(self) -> WindCase:
        """Deal when there are more than 3 WindForcePeriods."""
        wd_period_cnt: int = len(self.block.wd_periods)

        # self._sort_periods()
        self._concatenate_wf_periods()
        if wd_period_cnt == 0:
            return WindCase.CASE_3_1B_13
        if wd_period_cnt == 1:
            return WindCase.CASE_3_1B_11
        return WindCase.CASE_3_1B_12

    def _concatenate_wf_periods(self) -> None:
        """Concatenate wind force periods."""
        wf_period = reduce(lambda x, y: x + y, self.block.wf_periods)
        self.block.wf_periods = [wf_period]

    def _preprocess(self):
        """Preprocess the summary computation.

        This function gets the case nbr and add it in the summary.
        """
        wf_period_cnt: int = len(self.block.wf_periods)

        if wf_period_cnt == 0:
            raise WindSynthesisError("Type 3 block has no wind force periods !")

        case: WindCase

        if wf_period_cnt == 1:
            case = self._1_wind_force_period_process()

        elif wf_period_cnt == 2:
            case = self._2_wind_force_periods_process()

        else:  # ie self.wf_period_cnt > 2
            case = self._more_than_3_wind_force_periods_process()

        self.case = case
        self._set_summary_case(self.case)

    def _update_summary(self):
        """Update the summary attribute"""
        wf_period_cnt: int = len(self.block.wf_periods)

        # WindForcePeriods
        if wf_period_cnt == 0:
            raise ValueError("wf_period_cnt has to be > 0 !")
        if wf_period_cnt == 2:
            # set wind force variation marker
            wf_var_marker: str = self._get_wind_force_variation_marker(
                self.block.wf_periods[0].wind_element,
                self.block.wf_periods[1].wind_element,
            )
            self._summary[self.WF_VARIATION_MARKER] = wf_var_marker
        elif wf_period_cnt > 2:
            raise ValueError("wf_period_cnt can not to be > 2 !")

        # WindDirectionPeriods
        wd_period_cnt: int = len(self.block.wd_periods)

        if wd_period_cnt > 2:
            raise ValueError("wd_period_cnt can not be > 2 !")

    def compute(self, reference_datetime: Datetime) -> dict:
        """Compute block summary."""
        # Add block summary in the summary
        self._summary.update(self.block.summarize(reference_datetime))

        self._update_summary()

        return self._summary

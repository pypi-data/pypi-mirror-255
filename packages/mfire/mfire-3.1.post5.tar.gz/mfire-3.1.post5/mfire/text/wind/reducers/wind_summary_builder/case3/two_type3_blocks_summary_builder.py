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
from mfire.text.wind.reducers.wind_summary_builder.helpers.utils import (
    get_dict_value_from_keys_path,
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
    name="two_type3_blocks_summary_builder.mod", bind="two_type3_blocks_summary_builder"
)


class TwoType3BlocksSummaryBuilder(
    WindSummaryBuilderMixin, SummaryKeysMixin, SummaryValuesMixin
):
    """TwoType3BlocksSummaryBuilder class."""

    CHANGING_BLOCK_WF: str = "changing_block_wf"
    JUXTAPOSED_WFS: str = "juxtaposed_wfs"
    NOT_JUXTAPOSED_WFS: str = "not_juxtaposed_wfs"
    DIFFERENT_WDS: str = "different_wds"
    DIFFERENT_WFS: str = "different_wfs"
    SAME_WDS: str = "same_wds"
    SAME_WFS: str = "same_wfs"
    ONE_WF_PER_BLOCK: str = "one_wf_per_block"

    case_MAPPING: dict = {
        ONE_WF_PER_BLOCK: {
            SAME_WFS: {
                (1, 1): {
                    SAME_WDS: WindCase.CASE_3_2B_1,
                    DIFFERENT_WDS: WindCase.CASE_3_2B_2,
                },
                (1, 0): WindCase.CASE_3_2B_3,
                (0, 1): WindCase.CASE_3_2B_4,
                (2, 1): WindCase.CASE_3_2B_5,
                (2, 0): WindCase.CASE_3_2B_6,
                (1, 2): WindCase.CASE_3_2B_7,
                (0, 2): WindCase.CASE_3_2B_8,
                (2, 2): WindCase.CASE_3_2B_9,
                (0, 0): WindCase.CASE_3_2B_10,
            },
            DIFFERENT_WFS: {
                NOT_JUXTAPOSED_WFS: {
                    (1, 1): {
                        SAME_WDS: WindCase.CASE_3_2B_11,
                        DIFFERENT_WDS: WindCase.CASE_3_2B_13,
                    },
                    (1, 0): WindCase.CASE_3_2B_15,
                    (0, 1): WindCase.CASE_3_2B_17,
                    (2, 1): WindCase.CASE_3_2B_19,
                    (2, 0): WindCase.CASE_3_2B_21,
                    (1, 2): WindCase.CASE_3_2B_23,
                    (0, 2): WindCase.CASE_3_2B_25,
                    (2, 2): WindCase.CASE_3_2B_27,
                    (0, 0): WindCase.CASE_3_2B_29,
                },
                JUXTAPOSED_WFS: {
                    (1, 1): {
                        SAME_WDS: WindCase.CASE_3_2B_12,
                        DIFFERENT_WDS: WindCase.CASE_3_2B_14,
                    },
                    (1, 0): WindCase.CASE_3_2B_16,
                    (0, 1): WindCase.CASE_3_2B_18,
                    (2, 1): WindCase.CASE_3_2B_20,
                    (2, 0): WindCase.CASE_3_2B_22,
                    (1, 2): WindCase.CASE_3_2B_24,
                    (0, 2): WindCase.CASE_3_2B_26,
                    (2, 2): WindCase.CASE_3_2B_28,
                    (0, 0): WindCase.CASE_3_2B_30,
                },
            },
        },
        CHANGING_BLOCK_WF: {
            (1, 1): {
                SAME_WDS: WindCase.CASE_3_2B_31,
                DIFFERENT_WDS: WindCase.CASE_3_2B_32,
            },
            (1, 0): WindCase.CASE_3_2B_33,
            (0, 1): WindCase.CASE_3_2B_34,
            (2, 1): WindCase.CASE_3_2B_35,
            (2, 0): WindCase.CASE_3_2B_36,
            (1, 2): WindCase.CASE_3_2B_37,
            (0, 2): WindCase.CASE_3_2B_38,
            (2, 2): WindCase.CASE_3_2B_39,
            (0, 0): WindCase.CASE_3_2B_40,
        },
    }

    def __init__(self, blocks: list[WindBlock]):
        self.case: Optional[WindCase] = None
        self.blocks: list[WindBlock] = copy.deepcopy(blocks)
        self._wf_periods: list[WindForcePeriod] = []
        self._wd_periods: list[WindDirectionPeriod] = []
        self._mapping_path: list = []
        super().__init__()

        self._preprocess()

    @property
    def wf_periods(self) -> list[WindForcePeriod]:
        return self._wf_periods

    @wf_periods.setter
    def wf_periods(self, wf_periods: list[WindForcePeriod]) -> None:
        if self._check_times_of_periods(wf_periods) is False:
            return
        self._wf_periods = wf_periods

    @property
    def wd_periods(self) -> list[WindDirectionPeriod]:
        return self._wd_periods

    @wd_periods.setter
    def wd_periods(self, wd_periods: list[WindDirectionPeriod]) -> None:
        if self._check_times_of_periods(wd_periods) is False:
            return
        self._wd_periods = wd_periods

    def _check_period_times(
        self, period: WindForcePeriod | WindDirectionPeriod
    ) -> None:
        """Check a WindForcePeriod or a WindDirectionPeriod."""
        if period.begin_time < self.blocks[0].begin_time:
            raise WindSynthesisError(
                f"Input period.begin_time '{period.begin_time}' < block[0].begin_time "
                f"'{self.blocks[0].begin_time}' !"
            )

        if period.end_time > self.blocks[1].end_time:
            raise WindSynthesisError(
                f"Input period.end_time '{period.end_time}' is > block[1].end_time "
                f"'{self.blocks[1].end_time}' !"
            )

    def _check_times_of_periods(
        self, periods: list[WindForcePeriod] | list[WindDirectionPeriod]
    ) -> None:
        """Check begin_time and end_time of input periods."""
        for period in periods:
            self._check_period_times(period)

    def _check_wf_periods_of_block(self, ind: int) -> None:
        """Check the number of wf_periods."""
        if self.blocks[ind].wf_periods_cnt == 0:
            raise WindSynthesisError(
                f"There are no wind force periods in the {ind}-th block !"
            )

    def _get_case_from_mapping_path(self) -> WindCase:
        """Get the WindCase from the mapping path."""
        return get_dict_value_from_keys_path(self.case_MAPPING, self._mapping_path)

    def _get_wind_forces_periods(self) -> list[WindForce]:
        """Get WindForcePeriods of blocks."""

        wfs_set: set[WindForce] = set()

        for block in self.blocks:
            wfs: list[WindForce] = [
                block.wf_periods[i].wind_element for i in range(len(block.wf_periods))
            ]
            wfs_set.update(wfs)

        return list(wfs_set)

    def _get_blocks_wd_periods(self) -> list[WindDirectionPeriod]:
        """Get WindDirectionPeriods of blocks.

        For each block, if there is only one WindDirectionPeriod, just take it.
        If there is more periods, take the first and the last.
        """
        wd_periods: list[WindDirectionPeriod] = []

        for i in range(2):
            wd_periods_block: list[WindDirectionPeriod] = self.blocks[i].wd_periods
            wd_periods_len: int = len(wd_periods_block)

            if wd_periods_len in [0, 1]:
                pass
            else:
                wd_periods_block = [wd_periods_block[0], wd_periods_block[-1]]

            wd_periods.extend(wd_periods_block)

        return wd_periods

    def _1_wd_periods_per_block_processing(self):
        """Process the case when there is 1 WindDirectionPeriod per block."""
        LOGGER.debug("one_wd_periods_per_block_processing starts")

        # If the 2 WindDirectionPeriod have the same direction, then concatenate
        # these periods
        if (
            self.blocks[0]
            .wd_periods[0]
            .has_same_direction_than(self.blocks[1].wd_periods[0])
        ):
            # update dict_path
            self._mapping_path.append(self.SAME_WDS)
        else:
            # update dict_path
            self._mapping_path.append(self.DIFFERENT_WDS)

    def _wd_periods_simple_case_processing(self) -> None:
        """Process simply WindDirectionPeriods."""
        LOGGER.debug("wd_periods_simple_processing")

        wd_period_cnts: tuple[int, int] = (
            self.blocks[0].wd_periods_cnt,
            self.blocks[1].wd_periods_cnt,
        )

        self._mapping_path.append(wd_period_cnts)

        if wd_period_cnts == (1, 1):
            self._1_wd_periods_per_block_processing()

    def _same_wf_per_block_processing(self):
        """Process the case when the 2 block have the same WindForce."""
        LOGGER.debug("2_same_wind_forces_processing starts")

        # Update dict_path
        self._mapping_path.append(self.SAME_WFS)

        # Set wf_periods attribute
        self.wf_periods = [self.blocks[0].wf_periods[0], self.blocks[1].wf_periods[0]]

        self._wd_periods_simple_case_processing()

    def _2_juxtaposed_wind_forces_processing(self):
        """Process the case when the 2 block WindForce are juxtaposed."""
        LOGGER.debug("2_juxtaposed_wind_forces_processing starts")

        # update dict_path
        self._mapping_path.append(self.JUXTAPOSED_WFS)

        # Set juxtaposed wind force in the 2 block WIndForcePeriod
        wf = reduce(lambda x, y: x + y, self._get_wind_forces_periods())
        for i in range(2):
            self.blocks[i].wf_periods[0].wind_element = wf

        # Set wf_periods attribute
        self.wf_periods = [self.blocks[0].wf_periods[0], self.blocks[1].wf_periods[0]]

        self._wd_periods_simple_case_processing()

    def _2_not_juxtaposed_wind_forces_processing(self):
        """Process the case when the 2 block WindForce are not juxtaposed."""
        LOGGER.debug("2_not_juxtaposed_wind_forces_processing starts")

        self._mapping_path.append(self.NOT_JUXTAPOSED_WFS)

        # Set wf_periods attribute
        self.wf_periods = [self.blocks[0].wf_periods[0], self.blocks[1].wf_periods[0]]

        wd_period_cnts: tuple[int, int] = (
            self.blocks[0].wd_periods_cnt,
            self.blocks[1].wd_periods_cnt,
        )

        # update dict_path
        self._mapping_path.append(wd_period_cnts)

        if wd_period_cnts == (1, 1):
            self._1_wd_periods_per_block_processing()

    def _different_wind_force_per_block_processing(self):
        """Process the case when there are 1 different WindForce for each
        block."""
        LOGGER.debug("2_different_wind_forces_processing starts")

        # update dict_path
        self._mapping_path.append(self.DIFFERENT_WFS)

        # Check if the 2 WIndForcePeriod are juxtaposed
        if (
            self.blocks[0]
            .wf_periods[0]
            .is_juxtaposed_with(self.blocks[1].wf_periods[0])
            is True
        ):
            # update dict_path
            self._2_juxtaposed_wind_forces_processing()
        else:
            self._2_not_juxtaposed_wind_forces_processing()

    def _1_wind_force_periods_per_block_processing(self) -> None:
        """Process the case when there are 1 WindForcePeriod per block."""
        LOGGER.debug("2_wind_force_periods_processing starts")

        # update dict_path
        self._mapping_path.append(self.ONE_WF_PER_BLOCK)

        # If WF1 = WF2, then concatenate the 2 WIndForcePeriod
        if (
            self.blocks[0]
            .wf_periods[0]
            .has_same_force_than(self.blocks[1].wf_periods[0])
        ):
            self._same_wf_per_block_processing()

        else:
            self._different_wind_force_per_block_processing()

    def _block_with_variable_wf_processing(self) -> None:
        """Process the case when there are more than 2 WindForce in total."""
        LOGGER.debug("2_wind_force_periods_processing starts")

        # update dict_path
        self._mapping_path.append(self.CHANGING_BLOCK_WF)

        # Compute wind force sum
        wf = reduce(lambda x, y: x + y, self._get_wind_forces_periods())

        # Set in wf_periods a WindForcePeriod with wf for all block times
        for i in range(2):
            wf_period: WindForcePeriod = WindForcePeriod(
                self.blocks[i].begin_time,
                self.blocks[i].end_time,
                wf,
            )
            self.wf_periods.append(wf_period)

        self._wd_periods_simple_case_processing()

    def _preprocess(self) -> None:
        """Preprocess the summary computation.

        The preprocess function has 3 main goals:
        - check if all blocks has at least 1 WindForcePeriod
        - set the case nbr
        - get WindForcePeriods and WindDirectionPeriods which will be used to update
        the generated summary.
        """

        # Check if wf_period_cnt > 0 for each block. If not, set case to
        # WindCase.CASE_3_ERROR
        for i in range(2):
            if self._check_wf_periods_of_block(i) is False:
                return

        # If each block has only 1 WindForcePeriod
        if (self.blocks[0].wf_periods_cnt, self.blocks[1].wf_periods_cnt) == (1, 1):
            self._1_wind_force_periods_per_block_processing()

        # Else
        else:
            self._block_with_variable_wf_processing()

        # Set wd_periods attribute
        self.wd_periods = self._get_blocks_wd_periods()

        self.case = self._get_case_from_mapping_path()
        self._set_summary_case(self.case)

    def _add_wf_period_in_summary(self, reference_datetime: Datetime) -> None:
        """Add wf_period summaries in the summary."""

        wf_periods_cnt: int = len(self.wf_periods)

        if wf_periods_cnt == 0:
            raise WindSynthesisError("wf_periods_cnt attribute must be > 0 !")

        self._summary[self.WF_PERIODS] = [
            p.summarize(reference_datetime) for p in self.wf_periods
        ]

    def _add_wd_period_in_summary(self, reference_datetime: Datetime) -> None:
        """Add wd_period summaries in the summary."""
        self._summary[self.WD_PERIODS] = [
            p.summarize(reference_datetime) for p in self.wd_periods
        ]

    def compute(self, reference_datetime: Datetime) -> dict:
        """Compute block summary."""
        self._add_wf_period_in_summary(reference_datetime)
        self._add_wd_period_in_summary(reference_datetime)

        return self._summary

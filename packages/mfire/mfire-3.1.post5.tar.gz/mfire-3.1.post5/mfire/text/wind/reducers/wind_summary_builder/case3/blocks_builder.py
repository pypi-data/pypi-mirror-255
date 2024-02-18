from __future__ import annotations

from datetime import timedelta
from typing import Optional

import numpy as np
import pandas as pd

import mfire.utils.mfxarray as xr
from mfire.settings import get_logger
from mfire.text.wind.exceptions import WindSynthesisError
from mfire.text.wind.reducers.wind_summary_builder.helpers import (
    PandasWindSummary,
    WindType,
)
from mfire.text.wind.reducers.wind_summary_builder.wind_direction import (
    WindDirectionPeriodFinder,
)
from mfire.text.wind.reducers.wind_summary_builder.helpers.wind_period import (
    WindPeriodsInitializer,
)
from mfire.text.wind.reducers.wind_summary_builder.wind_force import (
    WindForce,
    WindForcePeriodFinder,
    WindForcePeriodsInitializer,
)
from mfire.utils.date import Datetime, Timedelta

from .wind_block import WindBlock
from .wind_direction_period_finder import HighWindDirectionPeriodFinder

LOGGER = get_logger(name="block_builder.mod", bind="block_builder")


class BlocksBuilder:
    """BlocksBuilder class."""

    BLOCKS_MERGE_TRIES: int = 1
    TIME_SLICE_12H: timedelta = Timedelta(hours=12)

    def __init__(self):
        """Initialize the BlocksBuilder.

        During the process, _ind attribute travels in the _blocks index and allow to
        update it.
        """
        self._blocks: list[WindBlock] = []
        self._ind: int = 0
        self._ind_max: int = 0

        self._blocks_nbr_max: int = 0
        self._period_between_t3_blocks_bound: Timedelta = Timedelta(hours=0)
        self._t3_block_duration_min: Timedelta = Timedelta(hours=0)

    @property
    def blocks(self) -> list[WindBlock]:
        """Get all blocks even low typed blocks."""
        return self._blocks

    @property
    def flagged_blocks(self) -> list[WindBlock]:
        """Get flagged blocks."""
        return [block for block in self.blocks if block.flag is True]

    def _reset(
        self,
        pd_summary: PandasWindSummary,
        blocks_nbr_max: Optional[int] = None,
    ):
        """Reset the _blocks attribute.

        At the end of this method, all blocks are flagged (ie has the True flag).
        """
        # Reset parameters
        self._set_parameters(pd_summary, blocks_nbr_max)

        # Reset blocks
        self._blocks: list[WindBlock] = self._initialize_wind_blocks(pd_summary)
        self._ind_max = len(self._blocks) - 1

    def _reset_ind(self, start: int = 0):
        """Reset _ind attribute."""
        self._ind = start

    @staticmethod
    def _get_monitoring_period_duration(pd_summary: PandasWindSummary) -> Timedelta:
        """Get the duration of the monitoring period."""
        time_start: Datetime = pd_summary.get_term_previous_time(pd_summary.index[0])
        time_stop: Datetime = Datetime(pd_summary.index[-1])

        if time_start == time_stop:
            LOGGER.warning(
                f"time_start = time_stop = {time_start} => period_duration forced to"
                f"Timedelta(hours=0) !"
            )
            return Timedelta(hours=1)

        period_duration: Timedelta = Timedelta(time_stop - time_start)
        return period_duration

    def _set_parameters(
        self, pd_summary: PandasWindSummary, blocks_nbr_max: Optional[int] = None
    ):
        """Set parameters."""
        # Get duration period
        period_duration: timedelta = self._get_monitoring_period_duration(pd_summary)

        # Set parameters
        self._blocks_nbr_max: int = int(np.ceil(period_duration / self.TIME_SLICE_12H))
        if blocks_nbr_max is not None:
            self._blocks_nbr_max = min(self._blocks_nbr_max, blocks_nbr_max)
        self._period_between_t3_blocks_bound: Timedelta = Timedelta(period_duration / 6)
        self._t3_block_duration_min: Timedelta = self._period_between_t3_blocks_bound

        LOGGER.debug(f"period_duration: {period_duration}")
        LOGGER.debug(f"blocks_nbr_max: {self._blocks_nbr_max}")
        LOGGER.debug(f"period_between_min: {self._period_between_t3_blocks_bound}")
        LOGGER.debug(f"block_duration_min: {self._t3_block_duration_min}")

    def _remove_block_from_ind(self, ind: int):
        """Remove block from index in self._blocks."""
        self._blocks.pop(ind)
        self._ind_max -= 1

    def _remove_current_block(self):
        """Remove the current block."""
        self._remove_block_from_ind(self._ind)

    @staticmethod
    def _create_wind_block(
        valid_times: list[np.datetime64],
        wind_type: WindType,
        pd_summary: PandasWindSummary,
    ) -> WindBlock:
        """Create a WindBlock from its valid times."""

        # Get previous_time and end_time from valid_times
        previous_time: np.datetime64 = pd_summary.data.loc[
            valid_times[0], pd_summary.COL_PREVIOUS_TIME
        ]
        end_time: np.datetime64 = valid_times[-1]

        block: WindBlock = WindBlock(
            Datetime(previous_time),
            Datetime(end_time),
            wind_type,
            flag=False,
        )

        return block

    def _initialize_wind_blocks(self, pd_summary: PandasWindSummary) -> list[WindBlock]:
        """Initialize WindBlocks.

        Get blocks with type 2 or 3 only (blocks with type 1 are not kept).
        """
        blocks = []

        # Get the location of type 2 and 3 terms only
        selection: pd.DataFrame = pd_summary.data[
            (pd_summary.data[pd_summary.COL_WT] == WindType.TYPE_2)
            | (pd_summary.data[pd_summary.COL_WT] == WindType.TYPE_3)
        ]

        if selection.empty is True:
            raise WindSynthesisError("No wind type 2 and 3 terms found !")

        valid_times: list[np.datetime64] = []
        cnt: int = 0

        wind_type_prev: WindType = WindType(
            selection.loc[selection.index[0], pd_summary.COL_WT]
        )

        # Get wind blocks
        for valid_time in selection.index:

            data_frame: pd.DataFrame = selection.loc[valid_time]
            wind_type_cur: WindType = WindType(data_frame[pd_summary.COL_WT])

            if wind_type_cur != wind_type_prev:
                blocks.append(
                    self._create_wind_block(valid_times, wind_type_prev, pd_summary)
                )

                wind_type_prev = wind_type_cur
                valid_times = []

                cnt += 1

            valid_times.append(valid_time)

            if valid_time == selection.index[-1]:
                blocks.append(
                    self._create_wind_block(valid_times, wind_type_prev, pd_summary)
                )

        return blocks

    @staticmethod
    def _compute_data_wf_terms_q95(
        pd_summary: PandasWindSummary, data_wf: xr.DataArray
    ) -> None:
        wfq_max: float = 0.0

        # Compute the Q95 of the wind force for all type 3 terms
        data_frame: pd.DataFrame = pd_summary.data[
            pd_summary.data[pd_summary.COL_WT] == WindType.TYPE_3
        ]

        for valid_time in data_frame.index:
            wfq: float = WindForce.data_array_to_value(
                data_wf.sel(valid_time=valid_time)
            )
            wfq = round(wfq, 2)
            pd_summary.data.loc[valid_time, pd_summary.COL_WFQ] = wfq
            wfq_max = max(wfq_max, wfq)

        # Store the Q95 max in pd_summary
        pd_summary.add_attr(pd_summary.WFQ_MAX, wfq_max)

    def _preprocess_wind_blocks(
        self, pd_summary: PandasWindSummary, data_wf: xr.DataArray
    ) -> None:
        """Preprocess WindBlocks.

        This method flags:
        - blocks which contains the term with the maximum of the wind force Q95
        - long type 3 blocks

        It initializes the wf_periods of all blocks too.
        """
        self._reset_ind()

        # Get the maximum Q95 of the term's wind force
        self._compute_data_wf_terms_q95(pd_summary, data_wf)
        wfq_max: np.float64 = pd_summary.data.attrs[pd_summary.WFQ_MAX]

        flag_set: bool = False
        wfq_found: bool = False

        # Set flag as True to WindBlocks which have the Q95 max
        for self._ind in range(self._ind_max + 1):
            block_cur: WindBlock = self._blocks[self._ind]

            # Get the wind force Q95 of terms of the current WindBlock
            data_frame: pd.DataFrame = pd_summary.data[
                (
                    pd_summary.data[pd_summary.COL_PREVIOUS_TIME]
                    >= block_cur.begin_time.as_np_dt64
                )
                & (pd_summary.index <= block_cur.end_time.as_np_dt64)
                & (pd_summary.data[pd_summary.COL_WT] == WindType.TYPE_3)
            ]
            wfq_max_cur: np.float64 = data_frame[pd_summary.COL_WFQ].max()

            # Flag block if possible
            if block_cur.wind_type == WindType.TYPE_3:
                if wfq_max_cur == wfq_max:
                    self._blocks[self._ind].flag = True
                    wfq_found = True
                    flag_set = True
                elif block_cur.duration >= self._t3_block_duration_min:
                    self._blocks[self._ind].flag = True
                    flag_set = True

            # Initialize wf_periods
            wfq_da: xr.DataArray = xr.DataArray(
                data=data_frame[pd_summary.COL_WFQ].values,
                dims=["valid_time"],
                coords={"valid_time": data_frame.index.values},
            )

            wf_periods = WindForcePeriodsInitializer.get_term_periods(
                wfq_da, pd_summary, data_frame.index
            )
            self._blocks[self._ind].wf_periods = wf_periods

        if flag_set is None:
            raise WindSynthesisError("No flagged WindBlock with type 3 found !")
        if wfq_found is None:
            raise WindSynthesisError("Q95 max not found in the WindBlock with type 3 !")

    @staticmethod
    def _check_block_type(wind_block: WindBlock, wind_type: WindType):
        if wind_block.wind_type != wind_type:
            raise ValueError(
                f"The following WindBlock has not the wanted WindType {wind_type}: "
                f"{wind_block}"
            )

    def _try_to_merge_current_flagged_block_with_previous_blocks(
        self,
    ) -> bool:

        if self._ind - 2 < 0:
            return False

        self._check_block_type(self._blocks[self._ind], WindType.TYPE_3)
        self._check_block_type(self._blocks[self._ind - 1], WindType.TYPE_2)
        self._check_block_type(self._blocks[self._ind - 2], WindType.TYPE_3)

        if self._blocks[self._ind - 1].duration >= self._period_between_t3_blocks_bound:
            return False

        for ind in [self._ind - 1, self._ind - 2]:
            self._blocks[self._ind] = self._blocks[self._ind].merge(self._blocks[ind])

        for ind in range(2):
            self._remove_block_from_ind(self._ind - 1)
            self._ind -= 1

        return True

    def _try_to_merge_current_flagged_block_with_next_blocks(
        self,
    ) -> bool:

        if self._ind + 2 > self._ind_max:
            return False

        self._check_block_type(self._blocks[self._ind], WindType.TYPE_3)
        self._check_block_type(self._blocks[self._ind + 1], WindType.TYPE_2)
        self._check_block_type(self._blocks[self._ind + 2], WindType.TYPE_3)

        if self._blocks[self._ind + 1].duration >= self._period_between_t3_blocks_bound:
            return False

        for ind in [self._ind + 1, self._ind + 2]:
            self._blocks[self._ind] = self._blocks[self._ind].merge(self._blocks[ind])

        for ind in range(2):
            self._remove_block_from_ind(self._ind + 1)

        return True

    def _merge_blocks(self):
        # Reset self._ind
        self._reset_ind()

        while self._ind <= self._ind_max:

            # Get next flagged WindBlock
            while self._ind <= self._ind_max and self._blocks[self._ind].flag is False:
                self._ind += 1

            # If ind max reached, stop the process
            if self._ind > self._ind_max:
                break

            # try to merge the current flagged WindBlock with its 2 previous blocks
            while True:
                if not self._try_to_merge_current_flagged_block_with_previous_blocks():
                    break

            # try to merge the current flagged WindBlock with its 2 last blocks
            while True:
                if not self._try_to_merge_current_flagged_block_with_next_blocks():
                    break

            self._ind += 1

        # Merge next to next unflagged blocks
        self._merge_side_by_side_unflagged_blocks()

        # Post-processing
        self._blocks_merging_post_process()

    def _merge_side_by_side_blocks_from_wind_type(self, wind_type: WindType) -> None:
        """Merge side by side blocks regarding a wind type."""
        self._reset_ind()

        while self._ind <= self._ind_max:

            block_cur: WindBlock = self._blocks[self._ind]

            if block_cur.wind_type == wind_type:

                j = self._ind + 1

                if j <= self._ind_max:
                    block_next: WindBlock = self._blocks[j]
                    if block_next.wind_type == wind_type:
                        block_cur = block_cur.merge(block_next)
                        self._blocks[j] = block_cur
                        self._remove_current_block()

            self._ind += 1

    def _merge_side_by_side_unflagged_blocks(self) -> None:
        """Merge side by side blocks regarding a flag."""
        self._reset_ind()

        while self._ind <= self._ind_max - 1:

            block_cur: WindBlock = self._blocks[self._ind]

            if block_cur.flag is False:

                j = self._ind + 1

                block_next: WindBlock = self._blocks[j]
                if block_next.flag is False:

                    block_t2: Optional[WindBlock] = None
                    block_other: Optional[WindBlock] = None

                    for block in [block_cur, block_next]:
                        if block.wind_type == 2 and block_t2 is None:
                            block_t2 = block
                        else:
                            block_other = block

                    if block_t2 is None:
                        raise WindSynthesisError(
                            f"Type 2  block not found when trying to merge unflagged "
                            f"blocks: {block_cur}, {block_next} !"
                        )

                    if (
                        block_other.wind_type == WindType.TYPE_3
                        and block_other.duration >= self._t3_block_duration_min
                    ):
                        raise WindSynthesisError(
                            f"Too longer WindBlocks of type 3 found when trying to "
                            f"merge unflagged blocks: {block_other} !"
                        )

                    self._blocks[self._ind] = block_t2.merge(block_other)
                    self._remove_block_from_ind(j)

                else:
                    self._ind += 1
            else:
                self._ind += 1

    def get_flagged_blocks_indices(self) -> tuple[list[int], int]:
        """Get the index of the flagged blocks."""
        flagged_blocks_ind: list[int] = []
        cnt: int = 0

        for i, block in enumerate(self._blocks):
            if block.flag is True:
                flagged_blocks_ind.append(i)
                cnt += 1

        return flagged_blocks_ind, cnt

    def _reduce_blocks_number(self) -> bool:
        """Reduce type 3 WindBlocks number by merging the 2 closest flagged blocks."""
        flagged_blocks_ind, t3_blocks_cnt = self.get_flagged_blocks_indices()
        space_min: Optional[Timedelta] = None
        ind: Optional[tuple[int, int]] = None

        for i in range(t3_blocks_cnt - 1):
            i0: int = flagged_blocks_ind[i]
            i1: int = flagged_blocks_ind[i + 1]

            space = self.blocks[i1].begin_time - self.blocks[i0].end_time
            if space_min is None or space < space_min:
                space_min = space
                ind = i0, i1

        # If a min space between 2 blocks has been found, then we merge those and keep
        # only the resulting block
        if ind is not None:
            i0, i1 = ind
            self.blocks[i1] = self.blocks[i0].merge(self.blocks[i1])

            for i in range(i0, i1):
                self._remove_block_from_ind(i0)

            return True

        return False

    def _blocks_merging_post_process(self) -> None:
        """Post-process the block merging."""
        flagged_blocks_cnt: int = len(self.flagged_blocks)

        if flagged_blocks_cnt == 0:
            raise WindSynthesisError("No blocks of type 3 have been found")

        elif flagged_blocks_cnt <= self._blocks_nbr_max:
            return

        else:
            # Reduce the number of type 3 WindBlocks if they are so much
            LOGGER.warning("A reduction of the Blocks number is needed")

            while flagged_blocks_cnt > self._blocks_nbr_max:
                reduce_res: bool = self._reduce_blocks_number()

                if reduce_res is False:
                    raise WindSynthesisError(
                        f"Failed to reduce the number of type 3 blocks "
                        f"to {self._blocks_nbr_max}"
                    )

                flagged_blocks_cnt: int = len(self.flagged_blocks)

    @staticmethod
    def _get_valid_time_of_block(
        block: WindBlock,
        pd_summary: PandasWindSummary,
        wind_types: Optional[list[WindType]] = None,
    ) -> pd.Index:
        """Get the valid_time of a block regarding its begin_time, end_time and type."""
        df_index: pd.Index = pd_summary.index

        if wind_types is None:
            wind_types = [block.wind_type]

        loc: pd.DataFrame = pd_summary.data[
            (
                pd_summary.data[pd_summary.COL_PREVIOUS_TIME]
                >= block.begin_time.as_np_dt64
            )
            & (df_index <= block.end_time.as_np_dt64)
            & (pd_summary.data[pd_summary.COL_WT].isin(wind_types))
        ]
        return loc.index

    def _get_periods_of_blocks(
        self,
        data_wd: xr.DataArray,
        pd_summary: PandasWindSummary,
    ) -> None:
        """Compute wind direction and force periods of blocks.

        For type 2 blocks, only the wind direction periods is computed.

        Raises
        ------
        ValueError
            If HighWindDirectionPeriodFinder instance raises a ValueError.
        """
        wp_initializer: WindPeriodsInitializer

        for i, block in enumerate(self._blocks):

            wind_direction_finder: WindDirectionPeriodFinder
            wind_force_finder: WindForcePeriodFinder

            if block.flag is False:

                # Get valid time of terms with type 2 or 3
                valid_times: pd.Index = self._get_valid_time_of_block(
                    block, pd_summary, [WindType.TYPE_2, WindType.TYPE_3]
                )

                # Get wind direction periods
                wind_direction_finder = WindDirectionPeriodFinder.from_data_array(
                    data_wd, pd_summary, valid_times
                )

                # Reset blocks wf_periods because it is not used
                self._blocks[i].wf_periods = []

            else:
                # Keep only terms with type 3
                valid_times: pd.Index = self._get_valid_time_of_block(
                    block, pd_summary, [WindType.TYPE_3]
                )

                # Get wind force periods
                wind_force_finder = WindForcePeriodFinder(self._blocks[i].wf_periods)
                self._blocks[i].wf_periods = wind_force_finder.run()

                # Get wind direction periods
                wind_direction_finder = HighWindDirectionPeriodFinder.from_data_array(
                    data_wd, pd_summary, valid_times
                )

            self._blocks[i].wd_periods = wind_direction_finder.run()

    def run(
        self,
        pd_summary: PandasWindSummary,
        data_wd: xr.DataArray,
        data_wf: xr.DataArray,
        blocks_nbr_max: Optional[int] = None,
    ) -> list[WindBlock]:
        """Run the builder.

        Its unflagged all resting low typed blocks (type 1 and 2) and all short type 3
        blocks as well.
        """
        # Reset blocks attributes
        self._reset(pd_summary, blocks_nbr_max)

        self._preprocess_wind_blocks(pd_summary, data_wf)

        self._merge_side_by_side_blocks_from_wind_type(WindType.TYPE_2)

        self._merge_blocks()

        # Get WindDirection and WindForce periods:
        # - wind force periods for type 3 blocks
        # - wind direction periods for type 2 and 3 blocks
        self._get_periods_of_blocks(data_wd, pd_summary)

        return self.blocks

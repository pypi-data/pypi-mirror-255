from __future__ import annotations

from datetime import timedelta

import mfire.utils.mfxarray as xr
from mfire.settings import get_logger
from mfire.text.wind.exceptions import WindSynthesisError, WindSynthesisNotImplemented
from mfire.text.wind.reducers.wind_summary_builder.base_case_summary_builder import (
    BaseCaseSummaryBuilder,
)
from mfire.text.wind.reducers.wind_summary_builder.helpers import (
    PandasWindSummary,
    WindSummaryBuilderMixin,
)
from mfire.utils.date import Datetime, Timedelta

from .blocks_builder import BlocksBuilder
from .one_type3_block_summary_builder import OneType3BlockSummaryBuilder
from .two_type3_blocks_summary_builder import TwoType3BlocksSummaryBuilder
from .wind_block import WindBlock

LOGGER = get_logger(name="case3_summary_builder.mod", bind="case3_summary_builder")


class Case3SummaryBuilder(WindSummaryBuilderMixin, BaseCaseSummaryBuilder):
    """Case3SummaryBuilder class."""

    BLOCKS_MERGE_TRIES: int = 5
    TIME_SLICE_12H: timedelta = Timedelta(hours=12)
    MAX_WIND_BLOCK_NBR: int = 2

    def __init__(
        self,
        pd_summary: PandasWindSummary,
        data_wd: xr.DataArray,
        data_wf: xr.DataArray,
    ):
        super().__init__()
        self.blocks_builder: BlocksBuilder = BlocksBuilder()

        # Run BlocksBuilder
        self.blocks_builder.run(pd_summary, data_wd, data_wf, self.MAX_WIND_BLOCK_NBR)

    def run(self, reference_datetime: Datetime) -> dict:
        """Run the summary builder."""

        blocks_ind: list[int]
        blocks_cnt: int

        # Get and check the counter of flagged blocks (type 3 blocks)
        blocks_ind, blocks_cnt = self.blocks_builder.get_flagged_blocks_indices()

        # If there is no type 3 block
        if blocks_cnt == 0:
            raise WindSynthesisError("No blocks of type 3 have been found")

        # If there is 1 type 3 block
        if blocks_cnt == 1:
            self._summary.update(
                OneType3BlockSummaryBuilder(
                    self.blocks_builder.blocks[blocks_ind[0]]
                ).compute(reference_datetime)
            )

        # If there is 2 blocks of type 3
        elif blocks_cnt == 2:
            blocks: list[WindBlock] = [
                self.blocks_builder.blocks[i] for i in blocks_ind
            ]
            self._summary.update(
                TwoType3BlocksSummaryBuilder(blocks).compute(reference_datetime)
            )

        # If there is more than 2 type 3 blocks
        else:
            raise WindSynthesisNotImplemented(
                "More than 2 blocks of type 3 have been found"
            )

        return self._summary

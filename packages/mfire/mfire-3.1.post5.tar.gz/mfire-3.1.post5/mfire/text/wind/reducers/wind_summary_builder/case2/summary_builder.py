from __future__ import annotations

import pandas as pd

import mfire.utils.mfxarray as xr
from mfire.settings import get_logger
from mfire.text.wind.reducers.wind_summary_builder.base_case_summary_builder import (
    BaseCaseSummaryBuilder,
)
from mfire.text.wind.reducers.wind_summary_builder.helpers import (
    BaseWindPeriod,
    PandasWindSummary,
    SummaryKeysMixin,
    SummaryValuesMixin,
    WindCase,
    WindSummaryBuilderMixin,
    WindType,
)
from mfire.text.wind.reducers.wind_summary_builder.wind_direction import (
    WindDirection,
    WindDirectionPeriodFinder,
)

LOGGER = get_logger(name="case2_summary_builder.mod", bind="case2_summary_builder")


class Case2SummaryBuilder(
    WindSummaryBuilderMixin,
    SummaryKeysMixin,
    SummaryValuesMixin,
    BaseCaseSummaryBuilder,
):
    def _get_wind_force_intensity(self, wind_types: set[WindType]) -> str:
        """Get the textual wind force intensity from the wind types."""

        if WindType.TYPE_1 in wind_types:
            return self.WF_INTENSITY_LOW_MIDDLE
        return self.WF_INTENSITY_MIDDLE

    def run(
        self,
        pd_summary: PandasWindSummary,
        reference_datetime,
        data_wd: xr.DataArray,
    ) -> dict:
        """Run the summary builder."""

        # Get wind directions with WindDirectionPeriodFinder
        data_frame: pd.DataFrame = pd_summary.data[
            pd_summary.data[pd_summary.COL_WT] == WindType.TYPE_2
        ]

        # Find WindDirectionPeriods
        wind_direction_finder = WindDirectionPeriodFinder.from_data_array(
            data_wd, pd_summary, data_frame.index
        )
        periods: list[BaseWindPeriod[WindDirection]] = wind_direction_finder.run()

        # Compute and return the summary
        self._summary = {
            self.WD_PERIODS: [p.summarize(reference_datetime) for p in periods],
            self.WF_INTENSITY: self._get_wind_force_intensity(
                pd_summary.wind_types_set
            ),
        }
        self._set_summary_case(WindCase.CASE_2)

        return self._summary

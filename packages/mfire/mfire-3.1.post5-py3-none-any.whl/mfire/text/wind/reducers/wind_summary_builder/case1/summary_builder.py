from __future__ import annotations

from mfire.settings import get_logger
from mfire.text.wind.reducers.wind_summary_builder.base_case_summary_builder import (
    BaseCaseSummaryBuilder,
)
from mfire.text.wind.reducers.wind_summary_builder.helpers import (
    WindCase,
    WindSummaryBuilderMixin,
)

LOGGER = get_logger(name="case1_summary_builder.mod", bind="case1_summary_builder")


class Case1SummaryBuilder(WindSummaryBuilderMixin, BaseCaseSummaryBuilder):
    """Case1SummaryBuilder class."""

    def run(self):
        """Run the summary builder."""
        self._set_summary_case(WindCase.CASE_1)
        return self._summary

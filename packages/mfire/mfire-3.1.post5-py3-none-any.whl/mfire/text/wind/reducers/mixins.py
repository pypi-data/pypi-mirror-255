from __future__ import annotations

from abc import ABC
from typing import Generic, Optional, TypeVar

from mfire.settings import get_logger
from mfire.text.wind.base.selectors import BaseSelector
from mfire.text.wind.const import ERROR_CASE

LOGGER = get_logger(
    name="wind_summary_build_helper_mixins.mod", bind="wind_summary_build_helper_mixins"
)


CaseEnum = TypeVar("CaseEnum")


class BaseSummaryBuilderMixin(ABC, Generic[CaseEnum]):
    """SummaryBuilderMixin class."""

    # TODO: create a inheriting class for wind and gust

    SELECTOR_KEY: str = BaseSelector.KEY

    def __init__(self):
        self._summary: dict = {}

    @property
    def case_value(self) -> Optional[str]:
        """Get the case value stored in the summary."""
        return self._summary.get(self.SELECTOR_KEY)

    def _set_summary_case(self, case: CaseEnum) -> None:
        """Set the wind case in the summary"""
        self._summary[self.SELECTOR_KEY] = case.value

    @classmethod
    def __add_problem_case_in_summary(cls, summary: dict, msg: str) -> None:
        """Add a case regarding a problem in the summary.

        A message msg is also added.
        """
        summary.update(
            {
                cls.SELECTOR_KEY: ERROR_CASE,
                "msg": msg,
            }
        )
        LOGGER.error(msg)

    @classmethod
    def _add_error_case_in_summary(cls, summary: dict, msg: str) -> None:
        """Add ERROR case nbr in summary."""
        cls.__add_problem_case_in_summary(summary, msg)

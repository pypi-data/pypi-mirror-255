from mfire.text.wind.reducers.mixins import BaseSummaryBuilderMixin
from mfire.text.wind.selectors import GustSelector

from .gust_enum import GustCase


class GustSummaryBuilderMixin(BaseSummaryBuilderMixin[GustCase]):

    SELECTOR_KEY: str = GustSelector.KEY

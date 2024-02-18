from mfire.settings import get_logger
from mfire.text.wind.base.selectors import BaseSelector

# Logging
LOGGER = get_logger(name="wind_selector.mod", bind="wind_selector")


class WindSelector(BaseSelector):
    """WindSelector class."""


class GustSelector(BaseSelector):
    """GustSelector class."""

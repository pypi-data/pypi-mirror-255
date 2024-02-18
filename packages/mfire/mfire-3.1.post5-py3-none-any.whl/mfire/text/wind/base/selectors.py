from abc import ABC

from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="base_selector.mod", bind="base_selector")


class BaseSelector(ABC):
    """BaseSelector class.

    Its indicates where is located the situation case in a summary.
    """

    KEY: str = "case"

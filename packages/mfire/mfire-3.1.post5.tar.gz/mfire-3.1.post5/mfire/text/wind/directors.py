"""WindDirector submodule."""

from mfire.settings import get_logger
from mfire.text.wind import WindBuilder, WindReducer
from mfire.text.wind.base import BaseDirector

# Logging
LOGGER = get_logger(name="wind_director.mod", bind="wind_director")


class WindDirector(BaseDirector):
    """WindDirector class."""

    REDUCER: WindReducer = WindReducer
    BUILDER: WindBuilder = WindBuilder
    WITH_EXTRA: bool = False

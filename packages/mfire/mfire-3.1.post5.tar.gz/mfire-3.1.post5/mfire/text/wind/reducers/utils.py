import numpy as np

from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="wind.reducers.utils.mod", bind="wind.reducers.utils")


def initialize_previous_time(valid_times: np.ndarray) -> np.datetime64:

    if len(valid_times) > 1:
        return valid_times[0] - (valid_times[1] - valid_times[0])

    LOGGER.warning("There is only one valid_time to compute wind text.")
    return valid_times[0] - np.timedelta64(1, "h")

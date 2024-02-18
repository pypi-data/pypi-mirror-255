from mfire.settings import get_logger
from mfire.text.base import BaseSelector

# Logging
LOGGER = get_logger(name="weather_selector.mod", bind="weather_selector")


class WeatherSelector(BaseSelector):
    """WeatherSelector specific to weather"""

    def compute(self, reduction: dict) -> str:
        """Generate the choice dictionary, search the synthesis text matrix
        for temperature to determine the template key based on the parameter.

        Args:
            reduction (dict): Reduction dictionary.

        Returns:
            str: Template key determined based on the parameter.
        """
        LOGGER.info(f"reduction {reduction}")

        nbr_ts: int = len(set(reduction) - {"TSsevere"})

        if nbr_ts == 0:
            return "0xTS"
        if nbr_ts == 1:
            key = "1xTS"
            if reduction["TS1"]["temporality"]:
                key += "_temp"
            if "TSsevere" in reduction:
                key += "_severe"
            return key
        if nbr_ts == 2:
            key = "2xTS"

            has_temp1 = reduction["TS1"]["temporality"] is not None
            has_temp2 = reduction["TS2"]["temporality"] is not None
            if has_temp1 or has_temp2:
                key += "_temp"
                if has_temp1 ^ has_temp2:
                    key += "1" if has_temp1 else "2"

            if "TSsevere" in reduction:
                key += "_severe"
            return key
        if nbr_ts == 3:
            key = "3xTS"
            has_temp1 = reduction["TS1"]["temporality"] is not None
            has_temp2 = reduction["TS2"]["temporality"] is not None
            has_temp3 = reduction["TS3"]["temporality"] is not None
            if has_temp1 or has_temp2 or has_temp3:
                key += "_temp"
                if has_temp1:
                    key += "1"
                if has_temp2:
                    key += "2"
                if has_temp3:
                    key += "3"
            return key

        return "Unimplemented"

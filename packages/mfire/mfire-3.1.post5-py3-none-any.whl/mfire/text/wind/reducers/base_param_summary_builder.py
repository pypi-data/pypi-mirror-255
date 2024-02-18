from abc import ABC, abstractmethod
from typing import Optional

import mfire.utils.mfxarray as xr
from mfire.composite import WeatherComposite
from mfire.settings import TEXT_ALGO
from mfire.utils.date import Datetime
from mfire.utils.unit_converter import unit_conversion


class BaseParamSummaryBuilder(ABC):
    """BaseParamSummaryBuilder."""

    USED_DIMS: list = ["valid_time", "latitude", "longitude"]

    @abstractmethod
    def __init__(self, compo: WeatherComposite, data_arrays: dict):
        pass

    @staticmethod
    def _get_composite_units(compo: WeatherComposite, param_name: str) -> str:
        """Get the units of the param regarding the WeatherComposite."""
        return compo.units.get(
            param_name,
            TEXT_ALGO[compo.id][compo.algorithm]["params"][param_name]["default_units"],
        )

    def _count_data_points(self, data: xr.DataArray) -> int:
        """Count the number of points of a term grid data."""
        latitude_size: int = int(data[self.USED_DIMS[1]].size)
        longitude_size: int = int(data[self.USED_DIMS[2]].size)
        return latitude_size * longitude_size

    @staticmethod
    def _get_data_array(
        data_array: xr.DataArray,
        param_name: str,
        units: Optional[str] = None,
        nan_replace: Optional[float] = None,
        values_to_replace: Optional[list[tuple[float, float]]] = None,
    ) -> xr.DataArray:
        """Clean and convert the input data_array."""
        # Get the data
        data_array = data_array[param_name]

        # Replace nan if necessary
        if nan_replace is not None:
            data_array = data_array.fillna(nan_replace)

        # Replace values if necessary
        if values_to_replace is not None:
            for value_old, value_new in values_to_replace:
                data_array = data_array.where(data_array != value_old, value_new)

        # Convert the data if asked
        if units:
            data_array = unit_conversion(data_array, units)

        return data_array

    @abstractmethod
    def compute(self, reference_datetime: Datetime) -> dict:
        """Compute the summary."""

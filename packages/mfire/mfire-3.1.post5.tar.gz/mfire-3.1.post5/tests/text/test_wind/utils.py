from typing import Optional, Union

import numpy as np

import mfire.utils.mfxarray as xr
from mfire.text.wind.reducers.wind_summary_builder import WindSummaryBuilder
from mfire.text.wind.reducers.wind_summary_builder.helpers import PandasWindSummary


def expand_array(array: np.ndarray, geos_desc_size: Optional[int] = None) -> np.ndarray:
    """Expand a numpy array to fit with dims of composite datasets."""
    size = []
    if geos_desc_size:
        size.append(geos_desc_size)
    size.extend([1, 1, 1])
    return np.tile(array, tuple(size))


def array_from_list(data: list, geos_desc_size: Optional[int] = None):
    array: np.ndarray = np.array(data)
    return expand_array(array, geos_desc_size)


def data_to_ndarray(
    data: Union[list, np.ndarray], expand: bool = True, expand_sz: Optional[int] = None
) -> np.ndarray:
    if isinstance(data, list):
        data = np.array(data)

    if expand:
        data = expand_array(data, expand_sz)

    return data


def create_param_data_array(
    data: Union[list, np.ndarray],
    valid_times: Union[list, np.ndarray],
    lon: list,
    lat: list,
) -> xr.DataArray:
    """Create a DataArray of wind param.

    The generated DataArray looks like GustSummaryBuilder.data or
    WindSummaryBuilder.data_wf or WindSummaryBuilder.data_wd attribute after when
    the summary builder instance has been created.
    """
    data_array: xr.DataArray = xr.DataArray(
        data,
        coords={
            "id": "0",
            "valid_time": valid_times,
            "latitude": lat,
            "longitude": lon,
            "areaType": "Axis",
            "areaName": "localisation 0",
        },
        dims=["valid_time", "latitude", "longitude"],
    )

    return data_array


def compute_threshold_accumulated(arrays_list) -> float:
    arrays = []

    for array in arrays_list:
        if isinstance(array, list):
            ndarray = np.array(array)
        elif isinstance(array, np.ndarray):
            ndarray = array
        else:
            raise TypeError

        ndarray[np.isnan(ndarray)] = 0.0
        arrays.append(ndarray)

    concatenation = np.concatenate(arrays, axis=None)

    res = np.percentile(concatenation, WindSummaryBuilder.WF_PERCENTILE_NUM) - 10

    return round(float(res), 1)


def compute_threshold_hours_max(arrays_list, terms_nbr: int):
    res = []

    if terms_nbr == 1:
        arrays_list = [arrays_list]

    for array in arrays_list:
        if isinstance(array, list):
            ndarray = np.array(array)
        elif isinstance(array, np.ndarray):
            ndarray = np.array(array)
        else:
            raise TypeError

        ndarray[np.isnan(ndarray)] = 0.0

        res.append(np.percentile(ndarray, WindSummaryBuilder.WF_PERCENTILE_NUM) - 10)

    return round(float(max(res)), 1)


def add_previous_time_in_pd_summary(
    pd_summary: PandasWindSummary, valid_times: np.ndarray
):
    # Initialize previous_time
    previous_time: np.datetime64
    if len(valid_times) > 1:
        previous_time = valid_times[0] - (valid_times[1] - valid_times[0])
    else:
        previous_time = valid_times[0] - np.timedelta64(1, "h")

    for valid_time in valid_times:
        pd_summary.data.loc[valid_time, pd_summary.COL_PREVIOUS_TIME] = previous_time
        previous_time = valid_time

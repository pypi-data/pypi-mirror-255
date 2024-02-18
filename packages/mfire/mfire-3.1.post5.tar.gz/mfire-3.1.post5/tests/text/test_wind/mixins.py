"""Unit tests of wind direction classes."""

import numpy as np
from typing import Union

from .utils import create_param_data_array


class CreateDataMixin:

    LON: list
    LAT: list

    @classmethod
    def _create_param_data_array(
        cls, data: Union[list, np.ndarray], valid_times: np.ndarray
    ):
        if len(cls.LON) == 1 and len(cls.LAT) == 1:
            data = [[[elt]] for elt in data]

        return create_param_data_array(data, valid_times, cls.LON, cls.LAT)


class Data1x1(CreateDataMixin):
    LON = [30]
    LAT = [40]


class Data2x2(CreateDataMixin):

    LON = [30, 31]
    LAT = [40, 41]

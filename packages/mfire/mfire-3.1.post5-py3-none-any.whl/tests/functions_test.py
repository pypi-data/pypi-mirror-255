from typing import Any, Union

import numpy as np
import xarray as xr

from mfire.utils.mfxarray import DataArray


def assert_identically_close(a: Any, b: Any):
    if a is None:
        assert b is None
        return

    assert type(a) == type(b)
    if isinstance(a, Union[xr.Dataset, DataArray]):
        if isinstance(a, DataArray) and any(np.array(a.shape) == 0):
            assert a.shape == b.shape
        else:
            xr.testing.assert_allclose(a, b)
        assert a.attrs == b.attrs
        for coord in a.coords:
            assert a[coord].attrs == b[coord].attrs

        if isinstance(a, xr.DataArray):
            assert a.name == b.name, f"Name are different: {a.name} != {b.name}"
    else:
        np.testing.assert_allclose(a, b)

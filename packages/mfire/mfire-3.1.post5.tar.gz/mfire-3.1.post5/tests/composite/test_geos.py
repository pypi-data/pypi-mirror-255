from unittest.mock import patch

import numpy as np
import pytest

import mfire.utils.mfxarray as xr
from mfire.settings import ALT_MAX, ALT_MIN
from tests.composite.factories import AltitudeCompositeFactory, GeoCompositeFactory
from tests.functions_test import assert_identically_close


class TestGeoComposite:
    def test_bounds(self):
        lon, lat = [30, 31, 32], [40, 41, 42]
        geos_da = xr.DataArray(
            np.random.rand(3, 3, 3),
            coords={"id": [1, 2, 3], "longitude": lon, "latitude": lat},
        )
        assert GeoCompositeFactory(data=geos_da).bounds == (30, 40, 32, 42)

    @patch("mfire.utils.xr_utils.MaskLoader.load")
    def test_compute(self, mock_func):
        mock_func.side_effect = lambda *args, **kwargs: (args, kwargs)
        geo = GeoCompositeFactory()
        assert geo.compute() == ((), {"ids_list": "mask_id"})


class TestAltitudeComposite:
    def test_init_alt_min(self, test_file):
        assert AltitudeCompositeFactory(alt_min=None).alt_min == ALT_MIN

    def test_init_alt_max(self, test_file):
        assert AltitudeCompositeFactory(alt_max=None).alt_max == ALT_MAX

    def test_default_init(self, test_file):
        with pytest.raises(FileNotFoundError, match="No such file test_file."):
            AltitudeCompositeFactory(filename="test_file")

    @pytest.mark.parametrize("test_file_path", [{"extension": "nc"}], indirect=True)
    def test_compute(self, test_file_path):
        lon, lat = [30], [40, 41, 42]
        da = xr.DataArray(
            data=[[125, 150, 175]],
            coords={"longitude": lon, "latitude": lat},
        )
        da.to_netcdf(test_file_path)

        altitude = AltitudeCompositeFactory(
            filename=test_file_path, alt_min=130, alt_max=160
        )

        result = altitude.compute()
        expected = xr.DataArray(
            data=[[np.nan, 150, np.nan]],
            coords={"longitude": lon, "latitude": lat},
        )
        assert_identically_close(result, expected)

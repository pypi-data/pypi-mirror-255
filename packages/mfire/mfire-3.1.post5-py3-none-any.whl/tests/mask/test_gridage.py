import numpy as np
import pytest
from shapely.geometry import shape as SHAshape

import mfire.utils.mfxarray as xr
from mfire.mask.gridage import GeoDraw, GeoTypeException
from mfire.utils.xr_utils import grid_info
from tests.functions_test import assert_identically_close


class TestGeoDraw:
    def test_lonlat2xy(self):
        ref_grid = {
            "conversion_slope": np.array([1 / 3.0, 1]),
            "conversion_offset": np.array([-0.5, -0.5]),
            "nb_c": 3,
            "nb_l": 2,
        }

        geodraw = GeoDraw(ref_grid)
        points = [[3, 1], [6, 2], [9, 1]]
        result = geodraw._lonlat2xy(points)
        # +0.5 to recentre grid
        ref_lonlat = [0.5, 0.5, 1.5, 1.5, 2.5, 0.5]
        assert result == ref_lonlat

    def test_create_mask_PIL(self):
        # create a grid
        nlt = 10
        nlg = 20
        value_da = np.random.rand(nlt, nlg)
        grid_da = xr.DataArray(
            data=value_da,
            coords={"latitude": np.arange(nlt), "longitude": np.arange(nlg)},
            dims=["latitude", "longitude"],
            name="grille",
        )

        # a single polygon
        poly = SHAshape(
            {
                "type": "Polygon",
                "coordinates": [[[1, 1], [1, 4], [3, 4], [3, 1], [1, 1]]],
            }
        )
        result = GeoDraw(grid_info(grid_da)).create_mask_PIL(poly)
        coords = {
            "latitude": ("latitude", [1, 2, 3, 4]),
            "longitude": ("longitude", [1, 2, 3]),
        }
        value = np.ones(12).astype("bool")
        value = value.reshape((4, 3))
        data_vars = {"grille": (["latitude", "longitude"], value)}
        ref_ds = xr.Dataset(
            data_vars=data_vars,
            coords=coords,
        )
        assert_identically_close(result, ref_ds)

        # a multi polygon
        poly = SHAshape(
            {
                "type": "MultiPolygon",
                "coordinates": [
                    [[[1, 1], [1, 4], [3, 4], [3, 1], [1, 1]]],
                    [[[5, 6], [5, 9], [8, 9], [8, 6], [5, 6]]],
                ],
            }
        )
        result = GeoDraw(grid_info(grid_da)).create_mask_PIL(poly)
        coords = {
            "latitude": ("latitude", [1, 2, 3, 4, 6, 7, 8, 9]),
            "longitude": ("longitude", [1, 2, 3, 5, 6, 7, 8]),
        }
        value = np.zeros(56).astype("bool")
        value = value.reshape((8, 7))
        value[0:4, 0:3] = True
        value[4:8, 3:7] = True
        data_vars = {"grille": (["latitude", "longitude"], value)}
        ref_ds = xr.Dataset(
            data_vars=data_vars,
            coords=coords,
        )
        assert_identically_close(result, ref_ds)

        # a polygon with a hole
        poly = SHAshape(
            {
                "type": "Polygon",
                "coordinates": [
                    [[1, 1], [1, 9], [9, 9], [9, 1], [1, 1]],
                    [[4, 4], [4, 6], [6, 6], [6, 4], [4, 4]],
                ],
            }
        )
        result = GeoDraw(grid_info(grid_da)).create_mask_PIL(poly)
        coords = {
            "latitude": ("latitude", [1, 2, 3, 4, 5, 6, 7, 8, 9]),
            "longitude": ("longitude", [1, 2, 3, 4, 5, 6, 7, 8, 9]),
        }
        value = np.ones(81).astype("bool")
        value = value.reshape((9, 9))
        value[3:6, 3:6] = False
        data_vars = {"grille": (["latitude", "longitude"], value)}
        ref_ds = xr.Dataset(
            data_vars=data_vars,
            coords=coords,
        )
        assert_identically_close(result, ref_ds)
        # a polygon which becomes a line
        poly = SHAshape(
            {
                "type": "Polygon",
                "coordinates": [
                    [[0.5, 0.9], [0.9, 4.1], [1.1, 4.1], [1.1, 0.9], [0.9, 0.9]]
                ],
            }
        )
        result = GeoDraw(grid_info(grid_da)).create_mask_PIL(poly)
        coords = {
            "latitude": ("latitude", [1, 2, 3, 4]),
            "longitude": ("longitude", [1]),
        }
        value = np.ones(4).astype("bool")
        value = value.reshape((4, 1))
        data_vars = {"grille": (["latitude", "longitude"], value)}
        ref_ds = xr.Dataset(
            data_vars=data_vars,
            coords=coords,
        )
        assert_identically_close(result, ref_ds)

        # a polygon which becomes a point
        poly = SHAshape(
            {
                "type": "Polygon",
                "coordinates": [
                    [[0.9, 0.9], [0.9, 1.1], [1.1, 1.1], [1.1, 0.9], [0.9, 0.9]]
                ],
            }
        )
        result = GeoDraw(grid_info(grid_da)).create_mask_PIL(poly)
        coords = {"latitude": ("latitude", [1]), "longitude": ("longitude", [1])}
        value = np.ones(1).astype("bool")
        value = value.reshape((1, 1))
        data_vars = {"grille": (["latitude", "longitude"], value)}
        ref_ds = xr.Dataset(
            data_vars=data_vars,
            coords=coords,
        )
        assert_identically_close(result, ref_ds)
        # a single line vertical/horizontal
        poly = SHAshape(
            {"type": "LineString", "coordinates": [[1, 1], [1, 2], [5, 2], [5, 1]]}
        )
        result = GeoDraw(grid_info(grid_da)).create_mask_PIL(poly)
        coords = {
            "latitude": (
                "latitude",
                [
                    1,
                    2,
                    3,
                ],
            ),
            "longitude": ("longitude", [1, 2, 3, 4, 5]),
        }
        value = np.ones(15).astype("bool")
        value = value.reshape((3, 5))
        value[0, 2] = False
        data_vars = {"grille": (["latitude", "longitude"], value)}
        ref_ds = xr.Dataset(
            data_vars=data_vars,
            coords=coords,
        )
        assert_identically_close(result, ref_ds)

        # a single line oblique
        poly = SHAshape({"type": "LineString", "coordinates": [[1, 1], [4, 8]]})
        result = GeoDraw(grid_info(grid_da)).create_mask_PIL(poly)
        coords = {
            "latitude": ("latitude", [1, 2, 3, 4, 5, 6, 7, 8]),
            "longitude": ("longitude", [1, 2, 3, 4, 5]),
        }
        value = np.zeros(40).astype("bool")
        value = value.reshape((8, 5))
        value[0:2, 0] = True
        value[0:4, 1] = True
        value[2:6, 2] = True
        value[4:8, 3] = True
        value[6:8, 4] = True
        data_vars = {"grille": (["latitude", "longitude"], value)}
        ref_ds = xr.Dataset(
            data_vars=data_vars,
            coords=coords,
        )
        assert_identically_close(result, ref_ds)

        # a multi line
        poly = SHAshape(
            {
                "type": "MultiLineString",
                "coordinates": [[[1, 1], [1, 4]], [[6, 4], [6, 1]]],
            }
        )
        result = GeoDraw(grid_info(grid_da)).create_mask_PIL(poly)
        coords = {
            "latitude": ("latitude", [1, 2, 3, 4]),
            "longitude": ("longitude", [1, 2, 5, 6]),
        }
        value = np.ones(16).astype("bool")
        value = value.reshape((4, 4))
        data_vars = {"grille": (["latitude", "longitude"], value)}
        ref_ds = xr.Dataset(
            data_vars=data_vars,
            coords=coords,
        )
        assert_identically_close(result, ref_ds)

        # a line which becomes a point
        poly = SHAshape(
            {"type": "LineString", "coordinates": [[0.9, 0.9], [0.9, 1.1], [1.1, 1.1]]}
        )
        result = GeoDraw(grid_info(grid_da)).create_mask_PIL(poly)
        coords = {"latitude": ("latitude", [1]), "longitude": ("longitude", [1])}
        value = np.ones(1).astype("bool")
        value = value.reshape((1, 1))
        data_vars = {"grille": (["latitude", "longitude"], value)}
        ref_ds = xr.Dataset(
            data_vars=data_vars,
            coords=coords,
        )
        assert_identically_close(result, ref_ds)

        # a single point
        poly = SHAshape({"type": "Point", "coordinates": [1.1, 1.1]})
        result = GeoDraw(grid_info(grid_da)).create_mask_PIL(poly)
        coords = {"latitude": ("latitude", [1]), "longitude": ("longitude", [1])}
        value = np.ones(1).astype("bool")
        value = value.reshape((1, 1))
        data_vars = {"grille": (["latitude", "longitude"], value)}
        ref_ds = xr.Dataset(
            data_vars=data_vars,
            coords=coords,
        )
        assert_identically_close(result, ref_ds)

        # a multi point
        poly = SHAshape(
            {"type": "MultiPoint", "coordinates": [[0.9, 0.9], [3.9, 1.1], [1.1, 2.1]]}
        )
        result = GeoDraw(grid_info(grid_da)).create_mask_PIL(poly)
        coords = {"latitude": ("latitude", [1, 2]), "longitude": ("longitude", [1, 4])}
        value = np.zeros(4).astype("bool")
        value = value.reshape((2, 2))
        value[0, 0] = True
        value[-1, 0] = True
        value[0, -1] = True
        data_vars = {"grille": (["latitude", "longitude"], value)}
        ref_ds = xr.Dataset(
            data_vars=data_vars,
            coords=coords,
        )
        assert_identically_close(result, ref_ds)

        # Linear ring without geoAction
        poly = SHAshape(
            {
                "type": "LinearRing",
                "coordinates": [(0, 0), (1, 1), (1, 0)],
            }
        )
        with pytest.raises(GeoTypeException, match="LinearRing"):
            GeoDraw(grid_info(grid_da)).create_mask_PIL(poly)

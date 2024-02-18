import numpy as np
import pytest

import mfire.utils.mfxarray as xr
from mfire.composite import AltitudeComposite, LocalisationConfig
from mfire.utils.date import Datetime
from tests.composite.factories import (
    AltitudeCompositeFactory,
    EventCompositeFactory,
    FieldCompositeFactory,
    GeoCompositeFactory,
    WeatherCompositeFactory,
)
from tests.functions_test import assert_identically_close


class TestWeatherComposite:
    def test_wrong_field(self):
        with pytest.raises(
            ValueError,
            match="Wrong field: [], expected ['wwmf', 'precip', 'rain', 'snow', 'lpn']",
        ):
            WeatherCompositeFactory(
                id="weather",
                params={},
            )

    def test_init_datetime(self):
        weather_compo = WeatherCompositeFactory(production_datetime="2023-03-01")
        assert weather_compo.production_datetime == Datetime(2023, 3, 1)

    def test_check_condition_without_condition(self):
        weather_compo = WeatherCompositeFactory()
        assert weather_compo.check_condition is False

    @pytest.mark.parametrize("values,expected", [([15, 16], False), ([15, 21], True)])
    def test_check_condition(self, values, expected):
        lon, lat = [15], [30]
        valid_time = [Datetime(2023, 3, i).as_np_dt64 for i in range(1, 3)]
        small_coords = {"longitude": lon, "latitude": lat}
        coords = small_coords | {"valid_time": valid_time}

        field_da = xr.DataArray(
            [
                [
                    [values[0], values[1]],
                ]
            ],
            coords=coords,
            attrs={"units": "mm"},
        )
        altitude_da = xr.DataArray([[1]], coords=small_coords)
        geos_da = xr.DataArray([[True]], coords=small_coords)

        field = FieldCompositeFactory(data=field_da)
        altitude = AltitudeCompositeFactory(data=altitude_da)
        geos = GeoCompositeFactory(data=geos_da)

        evt = EventCompositeFactory(
            field=field,
            geos=geos,
            altitude=altitude,
        )

        weather_compo = WeatherCompositeFactory(condition=evt)
        assert weather_compo.check_condition == expected

    def test_altitudes(self):
        weather_compo = WeatherCompositeFactory(
            id="tempe",
            params={"tempe": FieldCompositeFactory(grid_name="franxl1s100")},
        )

        assert weather_compo.altitudes("weather") is None

        alt = weather_compo.altitudes("tempe")
        assert isinstance(alt, xr.DataArray)
        assert alt.name == "franxl1s100"

    def test_geos_data(self):
        geos = GeoCompositeFactory(
            data=xr.DataArray([1, 2], coords={"id": ["id_1", "id_2"]})
        )
        weather_compo = WeatherCompositeFactory(geos=geos)
        assert_identically_close(
            weather_compo.geos_data(),
            xr.DataArray([1, 2], coords={"id": ["id_1", "id_2"]}),
        )
        assert_identically_close(
            weather_compo.geos_data(geo_id="id_1"),
            xr.DataArray(1, coords={"id": "id_1"}),
        )

    @pytest.mark.parametrize("test_file_path", [{"extension": "nc"}], indirect=True)
    def test_geos_descriptive(self, test_file_path):
        lon, lat = [31], [40]
        ids = ["id_axis", "id_1", "id_2", "id_axis_altitude", "id_axis_compass"]
        ds = xr.Dataset(
            {
                "A": (
                    ["longitude", "latitude", "id"],
                    [[[True, True, False, True, False]]],
                ),
            },
            coords={
                "id": ids,
                "longitude": lon,
                "latitude": lat,
                "areaType": (
                    ["id"],
                    ["areaTypeAxis", "areaType1", "areaType2", "Altitude", "compass"],
                ),
            },
        )
        ds.to_netcdf(test_file_path)

        weather_compo = WeatherCompositeFactory(
            geos=GeoCompositeFactory(file=test_file_path, grid_name="A"),
            localisation=LocalisationConfig(
                geos_descriptive=["id_1", "id_2"],
                compass_split=True,
                altitude_split=True,
            ),
        )
        assert_identically_close(
            weather_compo.geos_descriptive("id_axis"),
            xr.DataArray(
                [[[1.0, np.nan, 1.0, np.nan]]],
                coords={
                    "id": ["id_1", "id_2", "id_axis_altitude", "id_axis_compass"],
                    "longitude": lon,
                    "latitude": lat,
                    "areaName": (["id"], ["unknown", "unknown", "unknown", "unknown"]),
                    "areaType": (
                        ["id"],
                        ["areaType1", "areaType2", "Altitude", "compass"],
                    ),
                },
                dims=["longitude", "latitude", "id"],
                name="A",
            ),
        )

        weather_compo.localisation.compass_split = False
        weather_compo.localisation.altitude_split = False
        assert_identically_close(
            weather_compo.geos_descriptive("id_axis"),
            xr.DataArray(
                [[[1.0, np.nan]]],
                coords={
                    "id": ["id_1", "id_2"],
                    "longitude": lon,
                    "latitude": lat,
                    "areaName": (["id"], ["unknown", "unknown"]),
                    "areaType": (["id"], ["areaType1", "areaType2"]),
                },
                dims=["longitude", "latitude", "id"],
                name="A",
            ),
        )

    def test_compute(self):
        lon, lat = [35], [40, 41, 42]
        ids = ["id"]
        coords = {"id": ids, "longitude": lon, "latitude": lat}
        field_da = xr.DataArray([[[1.0, 2.0, 3.0]]], coords=coords)
        altitude_da = xr.DataArray([[[np.nan, 20.0, 30.0]]], coords=coords)
        geos_da = xr.DataArray([[[True, False, True]]], coords=coords)

        field = FieldCompositeFactory(data=field_da)
        altitude = AltitudeCompositeFactory(data=altitude_da)
        geos = GeoCompositeFactory(data=geos_da)

        weather_compo = WeatherCompositeFactory(
            id="tempe", params={"tempe": field}, altitude=altitude, geos=geos
        )

        expected = xr.Dataset(
            {
                "tempe": (["id", "longitude", "latitude"], [[[np.nan, np.nan, 3.0]]]),
                "altitude": (
                    ["id", "longitude", "latitude"],
                    [[[np.nan, np.nan, 30.0]]],
                ),
            },
            coords=coords
            | {"areaName": (["id"], ["unknown"]), "areaType": (["id"], ["unknown"])},
        )
        assert_identically_close(weather_compo.compute(geo_id=ids), expected)

    def test_from_grid_name(self):
        altitude = AltitudeComposite.from_grid_name(
            "franxl1s100", alt_min=15, alt_max=80
        )
        assert str(altitude.filename).endswith("franxl1s100.nc")
        assert altitude.alt_min == 15
        assert altitude.alt_max == 80

    def test_compute_with_small_geos(self):
        lon, lat = [35], [40, 41, 42]
        ids = ["id"]
        coords = {"id": ids, "longitude": lon, "latitude": lat}
        small_coords = {"id": ids, "longitude": lon, "latitude": [41]}

        field_da = xr.DataArray([[[1.0, 2.0, 3.0]]], coords=coords)
        altitude_da = xr.DataArray([[[30.0, 40.0, 50.0]]], coords=coords)
        geos_da = xr.DataArray([[[True]]], coords=small_coords)

        field = FieldCompositeFactory(data=field_da)
        altitude = AltitudeCompositeFactory(data=altitude_da)
        geos = GeoCompositeFactory(data=geos_da)

        weather_compo = WeatherCompositeFactory(
            id="tempe", params={"tempe": field}, altitude=altitude, geos=geos
        )

        expected = xr.Dataset(
            {
                "tempe": (["id", "longitude", "latitude"], [[[2.0]]]),
                "altitude": (["id", "longitude", "latitude"], [[[40.0]]]),
            },
            coords=small_coords
            | {"areaName": (["id"], ["unknown"]), "areaType": (["id"], ["unknown"])},
        )
        assert_identically_close(weather_compo.compute(geo_id=ids), expected)

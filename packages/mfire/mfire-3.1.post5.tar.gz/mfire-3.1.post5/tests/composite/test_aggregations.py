import pytest

import mfire.utils.mfxarray as xr
from mfire.composite import Aggregation
from mfire.composite.aggregations import AggregationMethod, Aggregator, InputError
from mfire.utils.date import Datetime
from tests.composite.factories import GeoCompositeFactory
from tests.functions_test import assert_identically_close


class TestAggregation:
    def test_default_kwargs(self):
        assert Aggregation(method=AggregationMethod.RDENSITY).kwargs == {"dr": 0.5}

        central_mask = GeoCompositeFactory()
        assert Aggregation(
            method=AggregationMethod.RDENSITY_WEIGHTED,
            kwargs={"central_mask": central_mask},
        ).kwargs == {
            "dr": 0.5,  # Le threshold par defaut
            "central_weight": 10,
            "outer_weight": 1,
            "central_mask": central_mask,
        }
        assert Aggregation(method=AggregationMethod.QUANTILE).kwargs == {"q": 0.5}

    def test_missing_key(self):
        with pytest.raises(ValueError) as err:
            Aggregation(
                method=AggregationMethod.RDENSITY_CONDITIONAL,
                kwargs={"dr": 0.5},
            )
        assert "Missing expected values: ['central_mask']" in str(err.value)

        with pytest.raises(ValueError) as err:
            Aggregation(
                method=AggregationMethod.RDENSITY_WEIGHTED,
                kwargs={"dr": 0.5},
            )
        assert "Missing expected values: ['central_mask']" in str(err.value)

    def test_unexpected_key(self):
        with pytest.raises(
            ValueError,
        ) as err:
            Aggregation(method=AggregationMethod.MEAN, kwargs={"dr": 0.5})
        assert "Unexpected values: ['dr']" in str(err.value)

        with pytest.raises(ValueError) as err:
            Aggregation(
                method=AggregationMethod.RDENSITY,
                kwargs={"dr": 0.5, "central_mask": GeoCompositeFactory()},
            )
        assert "Unexpected values: ['central_mask']" in str(err.value)

        with pytest.raises(ValueError) as err:
            Aggregation(
                method=AggregationMethod.RDENSITY_CONDITIONAL,
                kwargs={
                    "dr": 0.5,
                    "central_mask": GeoCompositeFactory(),
                    "central_weight": 1,
                    "outer_weight": 1,
                },
            )
        assert "Unexpected values: ['central_weight', 'outer_weight']" in str(err.value)

    def test_check_method_kwargs(self):
        agg = Aggregation(
            method=AggregationMethod.MEAN,
            kwargs={
                "dr": None,
                "central_weight": None,
                "outer_weight": None,
                "central_mask": None,
            },
        )
        assert isinstance(agg, Aggregation)
        assert agg.kwargs == {}


class TestAggregator:
    def test_compute_fails(self):
        agg = Aggregator(xr.DataArray())

        with pytest.raises(InputError, match="Threshold given = 1.5"):
            agg.compute(
                Aggregation(method=AggregationMethod.RDENSITY, kwargs={"dr": 1.5})
            )

        with pytest.raises(InputError, match="Threshold given = -1"):
            agg.compute(
                Aggregation(
                    method=AggregationMethod.RDENSITY_CONDITIONAL,
                    kwargs={"dr": -1, "central_mask": {}},
                )
            )

        with pytest.raises(InputError, match="Threshold given = -1"):
            agg.compute(
                Aggregation(
                    method=AggregationMethod.RDENSITY_WEIGHTED,
                    kwargs={
                        "dr": -1,
                        "central_mask": {},
                        "central_weight": 0.0,
                        "outer_weight": 0.0,
                    },
                )
            )

    def test_density(self):
        lon, lat = [31, 32], [40]
        valid_time = [Datetime(2023, 3, 1), Datetime(2023, 3, 2)]

        da = xr.DataArray(
            [[[0.1, 0.2], [0.3, 0.4]]],
            coords={"latitude": lat, "longitude": lon, "valid_time": valid_time},
        )
        agg_handler = Aggregator(da)
        agg = Aggregation(method=AggregationMethod.DENSITY)

        result = agg_handler.compute(agg)
        expected = xr.DataArray([0.2, 0.3], coords={"valid_time": valid_time})
        assert_identically_close(result, expected)

        agg_handler.aggregate_dim = "valid_time"
        result = agg_handler.compute(agg)
        expected = xr.DataArray(
            [[0.15, 0.35]], coords={"latitude": lat, "longitude": lon}
        )
        assert_identically_close(result, expected)

    def test_rdensity(self):
        lon, lat = [31, 32], [40]
        valid_time = [Datetime(2023, 3, 1), Datetime(2023, 3, 2)]

        da = xr.DataArray(
            [[[0.1, 0.2], [0.3, 0.4]]],
            coords={"latitude": lat, "longitude": lon, "valid_time": valid_time},
        )
        agg_handler = Aggregator(da)

        agg = Aggregation(method=AggregationMethod.RDENSITY, kwargs={"dr": 0.25})
        result = agg_handler.compute(agg)
        expected = xr.DataArray([False, True], coords={"valid_time": valid_time})
        assert_identically_close(result, expected)

        agg_handler.aggregate_dim = "valid_time"
        agg = Aggregation(method=AggregationMethod.RDENSITY, kwargs={"dr": 0.2})
        result = agg_handler.compute(agg)
        expected = xr.DataArray(
            [[False, True]], coords={"latitude": lat, "longitude": lon}
        )
        assert_identically_close(result, expected)

    @pytest.mark.parametrize("test_file_path", [{"extension": "nc"}], indirect=True)
    def test_drr_weighted(self, test_file_path):
        lon, lat = [15.0, 16.0], [17.0]
        valid_time = [Datetime(2023, 3, i).as_np_dt64 for i in range(1, 4)]
        ds = xr.Dataset(
            {
                "A": (["id", "latitude_monde", "longitude_glob05"], [[[True, False]]]),
            },
            coords={
                "id": ["id_central_mask"],
                "latitude_monde": lat,
                "longitude_glob05": lon,
            },
        )
        ds.to_netcdf(test_file_path)

        da = xr.DataArray(
            [[[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]]],
            coords={
                "id": ["id_area"],
                "latitude": lat,
                "longitude": lon,
                "valid_time": valid_time,
            },
            attrs={"PROMETHEE_z_ref": "A"},
        )
        agg_handler = Aggregator(da)
        agg = Aggregation(
            method=AggregationMethod.RDENSITY_WEIGHTED,
            kwargs={
                "dr": 0.2,
                "central_mask": {"file": test_file_path, "mask_id": "id_central_mask"},
                "central_weight": 0.5,
                "outer_weight": 0.1,
            },
        )

        result = agg_handler.compute(agg)
        expected = xr.DataArray(
            [[False, False, True]],
            coords={
                "id": ["id_area"],
                "valid_time": valid_time,
                "areaName": "unknown",
                "areaType": "unknown",
            },
            dims=["id", "valid_time"],
            attrs={"PROMETHEE_z_ref": "A"},
        )
        assert_identically_close(result, expected)

    @pytest.mark.parametrize("test_file_path", [{"extension": "nc"}], indirect=True)
    def test_drr_conditional(self, test_file_path):
        lon, lat = [15.0, 16.0], [17.0]
        valid_time = [Datetime(2023, 3, i).as_np_dt64 for i in range(1, 4)]
        ds = xr.Dataset(
            {
                "A": (["id", "latitude_monde", "longitude_glob05"], [[[True, False]]]),
            },
            coords={
                "id": ["id_central_mask"],
                "latitude_monde": lat,
                "longitude_glob05": lon,
            },
        )
        ds.to_netcdf(test_file_path)

        da = xr.DataArray(
            [[[[0, 0.2, 0.3], [0.4, 0.5, 0.6]]]],
            coords={
                "id": ["id_area"],
                "latitude": lat,
                "longitude": lon,
                "valid_time": valid_time,
            },
            attrs={"PROMETHEE_z_ref": "A"},
        )
        agg = Aggregation(
            method=AggregationMethod.RDENSITY_CONDITIONAL,
            kwargs={
                "dr": 0.4,
                "central_mask": {"file": test_file_path, "mask_id": "id_central_mask"},
            },
        )

        # Test without aggregate_dim
        result = Aggregator(da).compute(agg)
        expected = xr.DataArray(
            [[False, True, True]],
            coords={
                "id": ["id_area"],
                "valid_time": valid_time,
                "areaName": "unknown",
                "areaType": "unknown",
            },
            dims=["id", "valid_time"],
            attrs={"PROMETHEE_z_ref": "A"},
        )
        assert_identically_close(result, expected)

        # Test with aggregate_dim
        result = Aggregator(da, aggregate_dim="valid_time").compute(agg)
        expected = xr.DataArray(
            [[[True, True]]],
            coords={
                "id": ["id_area"],
                "latitude": lat,
                "longitude": lon,
                "areaName": "unknown",
                "areaType": "unknown",
            },
            dims=["id", "latitude", "longitude"],
            attrs={"PROMETHEE_z_ref": "A"},
        )
        assert_identically_close(result, expected)

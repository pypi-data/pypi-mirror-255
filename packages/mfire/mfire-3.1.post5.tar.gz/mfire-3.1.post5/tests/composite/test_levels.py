from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

import mfire.utils.mfxarray as xr
from mfire.composite import AggregationType, ComparisonOperator, LocalisationConfig
from mfire.composite.aggregations import AggregationMethod
from mfire.composite.events import Category, Threshold
from mfire.utils.date import Datetime
from tests.composite.factories import (
    AggregationFactory,
    AltitudeCompositeFactory,
    EventBertrandCompositeFactory,
    EventCompositeFactory,
    FieldCompositeFactory,
    GeoCompositeFactory,
    LevelCompositeFactory,
)
from tests.functions_test import assert_identically_close
from tests.utils.factories import SelectionFactory


class TestLevels:
    def test_grid_name(self):
        assert LevelCompositeFactory().grid_name == "franxl1s100"

    def test_geos_file(self):
        assert LevelCompositeFactory().geos_file == Path("geo_composite_file")

    def test_alt_min_and_alt_max(self):
        elements_event = [
            EventCompositeFactory(
                altitude=AltitudeCompositeFactory(alt_min=10, alt_max=200),
            ),
            EventCompositeFactory(
                altitude=AltitudeCompositeFactory(alt_min=50, alt_max=300)
            ),
        ]
        lvl = LevelCompositeFactory(
            elements_event=elements_event, logical_op_list=["or"]
        )

        assert lvl.alt_min == 10
        assert lvl.alt_max == 300

    @patch("mfire.utils.xr_utils.MaskLoader.load")
    def test_geos_descriptive(self, mock_func):
        lvl = LevelCompositeFactory(
            localisation=LocalisationConfig(geos_descriptive=["id_1", "id_2"])
        )
        mock_func.side_effect = lambda *args, **kwargs: (args, kwargs)
        assert lvl.geos_descriptive == ((), {"ids_list": ["id_1", "id_2"]})

    def test_mask_da(self):
        lon, lat = [15], [30, 31, 32, 33]
        valid_time = [Datetime(2023, 3, 1).as_np_dt64 for i in range(1, 3)]
        small_coords = {"longitude": lon, "latitude": lat}
        coords = small_coords | {"valid_time": valid_time}

        altitude_da = xr.DataArray([[10, np.nan, 20, 30]], coords=small_coords)
        altitude = AltitudeCompositeFactory(data=altitude_da)

        geos1_da = xr.DataArray([[False, True, True, True]], coords=small_coords)
        geos2_da = xr.DataArray([[False, True, False, True]], coords=small_coords)
        geos1 = GeoCompositeFactory(data=geos1_da)

        field = FieldCompositeFactory(
            data=xr.DataArray(np.random.random((1, 4, 2)), coords=coords),
        )

        evt1 = EventCompositeFactory(field=field, geos=geos1, altitude=altitude)
        evt2 = EventCompositeFactory(field=field, geos=geos2_da, altitude=altitude)
        lvl = LevelCompositeFactory(elements_event=[evt1, evt2], logical_op_list=["or"])

        expected = xr.DataArray([[np.nan, np.nan, 1.0, 1.0]], coords=small_coords)
        assert_identically_close(lvl.mask.f32, expected)

    @pytest.mark.parametrize("test_file_path", [{"extension": "nc"}], indirect=True)
    def test_cover_period(self, test_file_path):
        valid_time = [Datetime(2023, 3, i).as_np_dt64 for i in range(1, 4)]
        da = xr.DataArray(
            data=[1, 2, 3], coords={"valid_time": valid_time}, dims=["valid_time"]
        )
        da.to_netcdf(test_file_path)

        field_da = FieldCompositeFactory(file=test_file_path)
        elements_event = [
            EventCompositeFactory(field=field_da),
        ]
        lvl = LevelCompositeFactory(
            elements_event=elements_event,
        )

        np.testing.assert_array_equal(lvl.cover_period, valid_time)

    def test_update_selection(self):
        elements_event = [
            EventCompositeFactory(
                field=FieldCompositeFactory(selection=SelectionFactory())
            ),
            EventBertrandCompositeFactory(
                field=FieldCompositeFactory(selection=SelectionFactory())
            ),
        ]
        lvl = LevelCompositeFactory(
            elements_event=elements_event, logical_op_list=["or"]
        )
        new_selection = SelectionFactory()
        lvl.update_selection(
            new_sel=new_selection.sel,
            new_slice=new_selection.slice,
            new_isel=new_selection.isel,
            new_islice=new_selection.islice,
        )
        assert lvl.elements_event[0].field.selection == new_selection
        assert lvl.elements_event[1].field.selection == new_selection

        lvl.update_selection()  # does nothing
        assert lvl.elements_event[0].field.selection == new_selection
        assert lvl.elements_event[1].field.selection == new_selection

    def test_get_single_evt_comparison(self):
        lvl = LevelCompositeFactory(elements_event=[EventCompositeFactory()])

        expected = {
            "plain": Threshold(
                threshold=20, comparison_op=ComparisonOperator.SUPEGAL, units="mm"
            ),
            "category": Category.BOOLEAN,
            "aggregation": AggregationFactory(),
        }
        assert lvl.get_single_evt_comparison() == expected

    def test_get_comparison(self):
        evt1 = EventCompositeFactory(
            field=FieldCompositeFactory(name="field_1"),
            category=Category.QUANTITATIVE,
        )
        evt2 = EventCompositeFactory(
            plain=Threshold(
                threshold=3.1, comparison_op=ComparisonOperator.SUPEGAL, units="cm"
            ),
            mountain=Threshold(
                threshold=2.4, comparison_op=ComparisonOperator.SUP, units="cm"
            ),
            field=FieldCompositeFactory(name="field_2"),
        )
        evt3 = EventCompositeFactory(field=FieldCompositeFactory(name="field_2"))
        lvl = LevelCompositeFactory(
            elements_event=[evt1, evt2, evt3], logical_op_list=["or", "and"]
        )

        expected = {
            "field_1": {
                "plain": Threshold(
                    threshold=20, comparison_op=ComparisonOperator.SUPEGAL, units="mm"
                ),
                "category": Category.QUANTITATIVE,
                "aggregation": AggregationFactory(),
            },
            "field_2": {
                "plain": Threshold(
                    threshold=3.1, comparison_op=ComparisonOperator.SUPEGAL, units="cm"
                ),
                "category": Category.BOOLEAN,
                "mountain": Threshold(
                    threshold=2.4, comparison_op=ComparisonOperator.SUP, units="cm"
                ),
                "aggregation": AggregationFactory(),
            },
        }
        assert lvl.get_comparison() == expected

    def test_check_aggregation(self):
        agg = AggregationFactory()
        lvl = LevelCompositeFactory(
            aggregation_type=AggregationType.UP_STREAM, aggregation=agg
        )
        assert lvl.aggregation is None

        with pytest.raises(
            ValueError, match="Missing expected value 'aggregation' in level"
        ):
            _ = LevelCompositeFactory(
                aggregation_type=AggregationType.DOWN_STREAM, aggregation=None
            )

        lvl = LevelCompositeFactory(
            aggregation_type=AggregationType.DOWN_STREAM, aggregation=agg
        )
        assert lvl.aggregation == agg

    def test_check_nb_elements(self):
        elements_event = [EventCompositeFactory(), EventCompositeFactory()]
        logical_op_list = ["or"]

        lvl = LevelCompositeFactory(
            elements_event=elements_event, logical_op_list=logical_op_list
        )
        assert lvl.elements_event == elements_event

        with pytest.raises(
            ValueError,
            match="The number of logical operator is not "
            "consistent with the len of element list. "
            "Should be 1.",
        ):
            _ = LevelCompositeFactory(elements_event=elements_event, logical_op_list=[])

    def test_is_bertrand(self):
        lvl = LevelCompositeFactory(
            elements_event=[
                EventBertrandCompositeFactory(),
                EventBertrandCompositeFactory(),
            ],
            logical_op_list=["or"],
        )
        assert lvl.is_bertrand is True

        lvl = LevelCompositeFactory(
            elements_event=[EventCompositeFactory(), EventBertrandCompositeFactory()],
            logical_op_list=["or"],
        )
        assert lvl.is_bertrand is False

    @pytest.mark.parametrize("operator", ["or", "and"])
    def test_compute(self, operator, assert_equals_result):
        lon, lat = [15], [30, 31, 32, 33]
        valid_time = [Datetime(2023, 3, i).as_np_dt64 for i in range(1, 3)]
        ids = ["id"]
        small_coords = {"id": ids, "longitude": lon, "latitude": lat}
        coords = small_coords | {"valid_time": valid_time}

        altitude_da = xr.DataArray([[[10, np.nan, 20, 30]]], coords=small_coords)
        altitude = AltitudeCompositeFactory(data=altitude_da)

        geos1_da = xr.DataArray([[[False, True, True, True]]], coords=small_coords)
        geos2_da = xr.DataArray([[[False, True, False, True]]], coords=small_coords)
        geos1 = GeoCompositeFactory(data=geos1_da)
        geos2 = GeoCompositeFactory(data=geos2_da, grid_name=None)

        field = FieldCompositeFactory(
            data=xr.DataArray(
                [
                    [
                        [
                            [1000, 2000],  # masked values by geos
                            [1500, 3000],  # masked values by altitude
                            [1.7, 1.9],  # isn't risked with threshold and geos
                            [1.8, 1.9],
                        ]
                    ]
                ],
                coords=coords,
                attrs={"units": "cm"},
            ),
            grid_name="new_grid_name",
            name="NEIPOT24__SOL",
        )
        evt1 = EventCompositeFactory(
            field=field,
            geos=geos1,
            altitude=altitude,
            plain=Threshold(
                threshold=2.0, comparison_op=ComparisonOperator.SUPEGAL, units="cm"
            ),
        )
        evt2 = EventCompositeFactory(
            field=field,
            geos=geos2,
            altitude=altitude,
            plain=Threshold(
                threshold=15, comparison_op=ComparisonOperator.SUPEGAL, units="mm"
            ),
        )

        lvl = LevelCompositeFactory(
            elements_event=[evt1, evt2],
            logical_op_list=[operator],
        )

        result = lvl.compute()
        assert_equals_result(
            {
                "result": result.to_dict(),
                "spatial_risk_da": lvl.spatial_risk_da.to_dict(),
            }
        )

    @pytest.mark.parametrize("test_file_path", [{"extension": "nc"}], indirect=True)
    @pytest.mark.parametrize(
        "aggregation",
        [
            AggregationFactory(),
            AggregationFactory(method=AggregationMethod.DENSITY),
            AggregationFactory(method=AggregationMethod.MAX),
            AggregationFactory(method=AggregationMethod.RDENSITY),
            AggregationFactory(
                method=AggregationMethod.RDENSITY_WEIGHTED, kwargs={"central_mask": ...}
            ),
            AggregationFactory(
                method=AggregationMethod.RDENSITY_CONDITIONAL,
                kwargs={"central_mask": ...},
            ),
        ],
    )
    @pytest.mark.parametrize("operator", ["or", "and"])
    def test_compute_with_down_stream(
        self, aggregation, operator, test_file_path, assert_equals_result
    ):
        lon, lat = [15], [30, 31, 32, 33]
        valid_time = [Datetime(2023, 3, i).as_np_dt64 for i in range(1, 3)]
        ids = ["id"]
        small_coords = {"id": ids, "longitude": lon, "latitude": lat}
        coords = small_coords | {"valid_time": valid_time}

        # Create a central_mask for aggregations RDENSITY_WEIGHTED and
        # RDENSITY_CONDITIONAL
        if "central_mask" in aggregation.kwargs:
            ds = xr.Dataset(
                {
                    "A": (
                        ["id", "longitude_glob05", "latitude_monde"],
                        [[[True, True, False, False]]],
                    ),
                },
                coords={"id": ids, "longitude_glob05": lon, "latitude_monde": lat},
            )
            ds.to_netcdf(test_file_path)
            aggregation.kwargs["central_mask"] = {
                "file": test_file_path,
                "mask_id": ids[0],
            }

        altitude_da = xr.DataArray([[[10, np.nan, 20, 30]]], coords=small_coords)
        altitude = AltitudeCompositeFactory(data=altitude_da)

        geos1_da = xr.DataArray([[[False, True, True, True]]], coords=small_coords)
        geos2_da = xr.DataArray([[[False, True, False, True]]], coords=small_coords)
        geos1 = GeoCompositeFactory(data=geos1_da)
        geos2 = GeoCompositeFactory(data=geos2_da, grid_name=None)

        field = FieldCompositeFactory(
            data=xr.DataArray(
                [
                    [
                        [
                            [1000, 2000],  # masked values by geos
                            [1500, 3000],  # masked values by altitude
                            [1.7, 1.9],  # isn't risked with threshold and geos
                            [1.8, 1.9],
                        ]
                    ]
                ],
                coords=coords,
                attrs={"units": "cm", "PROMETHEE_z_ref": "A"},
            ),
            grid_name="new_grid_name",
            name="NEIPOT24__SOL",
        )
        evt1 = EventCompositeFactory(
            field=field,
            geos=geos1,
            altitude=altitude,
            plain=Threshold(
                threshold=2.0, comparison_op=ComparisonOperator.SUPEGAL, units="cm"
            ),
        )
        evt2 = EventCompositeFactory(
            field=field,
            geos=geos2,
            altitude=altitude,
            plain=Threshold(
                threshold=15, comparison_op=ComparisonOperator.SUPEGAL, units="mm"
            ),
        )

        lvl = LevelCompositeFactory(
            aggregation=aggregation,
            aggregation_type=AggregationType.DOWN_STREAM,
            compute_list=["density", "summary"],
            elements_event=[evt1, evt2],
            logical_op_list=[operator],
        )

        result = lvl.compute()

        assert_equals_result(
            {
                "result": result.to_dict(),
                "occurrence_event": result.occurrence_event.to_dict(),
                "occurrence": result.occurrence.to_dict(),
                "spatial_risk_da": lvl.spatial_risk_da.to_dict(),
            }
        )

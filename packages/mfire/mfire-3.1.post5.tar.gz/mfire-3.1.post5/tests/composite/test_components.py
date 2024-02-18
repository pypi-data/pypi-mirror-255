from pathlib import Path

import numpy as np
import pytest

import mfire.utils.mfxarray as xr
from mfire.composite import (
    AggregationType,
    ComparisonOperator,
    Period,
    RiskComponentComposite,
    TextComponentComposite,
    Threshold,
)
from mfire.composite.aggregations import AggregationMethod
from mfire.composite.events import Category
from mfire.utils import JsonFile
from mfire.utils.date import Datetime
from tests.composite.factories import (
    AggregationFactory,
    AltitudeCompositeFactory,
    EventCompositeFactory,
    FieldCompositeFactory,
    GeoCompositeFactory,
    LevelCompositeFactory,
    RiskComponentCompositeFactory,
    TextComponentCompositeFactory,
    WeatherCompositeFactory,
)
from tests.functions_test import assert_identically_close


class TestAbstractComponentComposite:
    def test_init_dates(self):
        component = TextComponentCompositeFactory(
            production_datetime="2023-03-01", configuration_datetime="2023-03-02"
        )
        assert component.production_datetime == Datetime(2023, 3, 1)
        assert component.configuration_datetime == Datetime(2023, 3, 2)


class TestTextComponentComposite:
    inputs_dir: Path = Path(__file__).parent / "inputs"

    def test_weather_period(self):
        compo = TextComponentCompositeFactory()
        assert compo.weather_period == Period(
            id="period_id",
            start=Datetime(2023, 3, 1),
            stop=Datetime(2023, 3, 5),
        )

    def test_geo_name(self):
        ds = xr.Dataset(
            {"areaName": (["id"], ["area1", "area2"]), "id": ["id1", "id2"]}
        )
        text_compo = TextComponentCompositeFactory(data=ds)

        assert text_compo.geo_name("id1") == "area1"
        assert text_compo.geo_name("id2") == "area2"

    def test_compute(self):
        lon, lat = [35], [40, 41, 42]
        ids = ["id"]
        coords = {"id": ids, "longitude": lon, "latitude": lat}

        altitude_da = xr.DataArray([[[np.nan, 20.0, 30.0]]], coords=coords)
        altitude = AltitudeCompositeFactory(data=altitude_da)

        # First weather composite
        field1_da = xr.DataArray([[[1.0, 2.0, 3.0]]], coords=coords)
        geos1_da = xr.DataArray([[[True, False, True]]], coords=coords)

        field1 = FieldCompositeFactory(data=field1_da, name="T__HAUTEUR2")
        geos1 = GeoCompositeFactory(data=geos1_da)

        weather_compo1 = WeatherCompositeFactory(
            id="tempe", params={"tempe": field1}, altitude=altitude, geos=geos1
        )

        # Second weather composite
        field2_da = xr.DataArray([[[4.0, 5.0, 6.0]]], coords=coords)
        geos2_da = xr.DataArray([[[True, True, False]]], coords=coords)

        field2 = FieldCompositeFactory(data=field2_da, name="T__SOL")
        geos2 = GeoCompositeFactory(data=geos2_da)

        weather_compo2 = WeatherCompositeFactory(
            id="tempe", params={"tempe": field2}, altitude=altitude, geos=geos2
        )

        # Text Component
        text_compo = TextComponentCompositeFactory(
            geos=["id"], weathers=[weather_compo1, weather_compo2]
        )

        result = text_compo.compute()
        expected = xr.Dataset(
            {
                "tempe": (["id", "longitude", "latitude"], [[[np.nan, 5.0, 3.0]]]),
                "altitude": (
                    ["id", "longitude", "latitude"],
                    [[[np.nan, 20.0, 30.0]]],
                ),
            },
            coords=coords
            | {"areaName": (["id"], ["unknown"]), "areaType": (["id"], ["unknown"])},
        )
        assert_identically_close(result, expected)

    def test_integration(self, assert_equals_result, root_path_cwd):
        data = JsonFile(self.inputs_dir / "small_conf_text.json").load()
        data_prod = next(iter(data.values()))
        component = data_prod["components"][0]
        compo = TextComponentComposite(**component)

        assert_equals_result(compo)


class TestRiskComponentComposite:
    inputs_dir: Path = Path(__file__).parent / "inputs"

    def test_is_risks_empty(self):
        risk_compo = RiskComponentCompositeFactory()
        assert risk_compo.is_risks_empty is True

        risk_compo._risks_ds = xr.Dataset({"A": ("B", [1])}, coords={"B": [2]})
        assert risk_compo.is_risks_empty is False

    def test_risks_of_level(self):
        risk_compo = RiskComponentCompositeFactory(
            levels=[LevelCompositeFactory(level=1)] * 3
            + [LevelCompositeFactory(level=2)] * 5
        )
        assert len(risk_compo.risks_of_level(1)) == 3
        assert len(risk_compo.risks_of_level(2)) == 5
        assert len(risk_compo.risks_of_level(3)) == 0

    def test_final_risk_max_level(self):
        risk_compo = RiskComponentCompositeFactory()
        assert risk_compo.final_risk_max_level(geo_id="id") == 0

        da = xr.DataArray(
            [[1, 2], [4, 5]], coords={"id": ["id_1", "id_2"], "A": [3, 4]}
        )
        risk_compo._risks_ds = xr.Dataset({"A": ("B", [1])}, coords={"B": [2]})
        risk_compo._final_risk_da = da

        assert risk_compo.final_risk_max_level(geo_id="id_1") == 2
        assert risk_compo.final_risk_max_level(geo_id="id_2") == 5

    def test_final_risk_min_level(self):
        risk_compo = RiskComponentCompositeFactory()
        assert risk_compo.final_risk_min_level(geo_id="id") == 0

        da = xr.DataArray(
            [[1, 2], [4, 5]], coords={"id": ["id_1", "id_2"], "A": [3, 4]}
        )
        risk_compo._risks_ds = xr.Dataset({"A": ("B", [1])}, coords={"B": [2]})
        risk_compo._final_risk_da = da

        assert risk_compo.final_risk_min_level(geo_id="id_1") == 1
        assert risk_compo.final_risk_min_level(geo_id="id_2") == 4

    def test_geo_name(self):
        risk_compo = RiskComponentCompositeFactory()
        assert risk_compo.geo_name(geo_id="id") == "N.A"

        risk_compo._risks_ds = xr.Dataset(
            {"areaName": (["id"], ["area1", "area2"])}, coords={"id": ["id1", "id2"]}
        )
        assert risk_compo.geo_name(geo_id="id1") == "area1"
        assert risk_compo.geo_name(geo_id="id2") == "area2"

    def test_get_comparison(self):
        levels = [
            LevelCompositeFactory(
                level=1,
                elements_event=[
                    EventCompositeFactory(
                        plain=Threshold(
                            threshold=13,
                            comparison_op=ComparisonOperator.SUP,
                            units="mm",
                        ),
                        mountain=Threshold(
                            threshold=13,
                            comparison_op=ComparisonOperator.INF,
                            units="mm",
                        ),
                    )
                ],
            ),
            LevelCompositeFactory(
                level=2,
                elements_event=[
                    EventCompositeFactory(
                        plain=Threshold(
                            threshold=1.5,
                            comparison_op=ComparisonOperator.SUP,
                            units="cm",
                        ),
                        mountain=Threshold(
                            threshold=1.0,
                            comparison_op=ComparisonOperator.INF,
                            units="cm",
                        ),
                    )
                ],
            ),
            LevelCompositeFactory(
                level=3,
                elements_event=[
                    EventCompositeFactory(
                        plain=Threshold(
                            threshold=20,
                            comparison_op=ComparisonOperator.SUP,
                            units="mm",
                        ),
                        mountain=Threshold(
                            threshold=0.5,
                            comparison_op=ComparisonOperator.INF,
                            units="cm",
                        ),
                    )
                ],
            ),
        ]
        risk_compo = RiskComponentCompositeFactory(levels=levels)
        assert risk_compo.get_comparison(1) == {
            "field_name": {
                "plain": Threshold(
                    threshold=13,
                    comparison_op=ComparisonOperator.SUP,
                    units="mm",
                    next_critical=15.0,
                ),
                "category": Category.BOOLEAN,
                "mountain": Threshold(
                    threshold=13,
                    comparison_op=ComparisonOperator.INF,
                    units="mm",
                    next_critical=10.0,
                ),
                "aggregation": {"kwargs": {}, "method": AggregationMethod.MEAN},
            }
        }
        assert risk_compo.get_comparison(2) == {
            "field_name": {
                "plain": Threshold(
                    threshold=1.5,
                    comparison_op=ComparisonOperator.SUP,
                    units="cm",
                    next_critical=2.0,
                ),
                "category": Category.BOOLEAN,
                "mountain": Threshold(
                    threshold=1,
                    comparison_op=ComparisonOperator.INF,
                    units="cm",
                    next_critical=0.5,
                ),
                "aggregation": {"kwargs": {}, "method": AggregationMethod.MEAN},
            }
        }
        assert risk_compo.get_comparison(3) == {
            "field_name": {
                "plain": Threshold(
                    threshold=20,
                    comparison_op=ComparisonOperator.SUP,
                    units="mm",
                ),
                "category": Category.BOOLEAN,
                "mountain": Threshold(
                    threshold=0.5,
                    comparison_op=ComparisonOperator.INF,
                    units="cm",
                ),
                "aggregation": {"kwargs": {}, "method": AggregationMethod.MEAN},
            }
        }

    @pytest.mark.parametrize(
        "axis,expected",
        [
            (0, [5.0, 1.0, 4.0]),
            (1, [2.0, 4.0, 4.0]),
            ((0,), [5.0, 1.0, 4.0]),
            ((1,), [2.0, 4.0, 4.0]),
        ],
    )
    def test_replace_middle(self, axis, expected):
        x = np.array([[2.0, 1.0, 2.0], [5.0, 1.0, 4.0], [4.0, 4.0, 1.0]])
        result = RiskComponentComposite._replace_middle(x, axis=axis)
        assert_identically_close(result, np.array(expected))

    def test_compute(self, assert_equals_result):
        lon, lat = [15], [30, 31, 32, 33]
        ids = ["id"]
        small_coords = {"id": ids, "longitude": lon, "latitude": lat}

        altitude_da = xr.DataArray([[[10, np.nan, 20, 30]]], coords=small_coords)
        altitude = AltitudeCompositeFactory(data=altitude_da)

        geos1_da = xr.DataArray([[[False, True, True, True]]], coords=small_coords)
        geos2_da = xr.DataArray([[[False, True, False, True]]], coords=small_coords)
        geos1 = GeoCompositeFactory(data=geos1_da)
        geos2 = GeoCompositeFactory(data=geos2_da, grid_name=None)

        field1 = FieldCompositeFactory(
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
                coords=small_coords
                | {
                    "valid_time": [Datetime(2023, 3, i).as_np_dt64 for i in range(1, 3)]
                },
                attrs={"units": "cm"},
            ),
            grid_name="new_grid_name",
            name="NEIPOT24__SOL",
        )
        field2 = FieldCompositeFactory(
            data=xr.DataArray(
                [
                    [
                        [
                            [1500],  # masked values by geos
                            [2000],  # masked values by altitude
                            [1.6],  # isn't risked with threshold
                            [1.9],
                        ]
                    ]
                ],
                coords=small_coords | {"valid_time": [Datetime(2023, 3, 3).as_np_dt64]},
                attrs={"units": "cm"},
            ),
            grid_name="new_grid_name",
            name="NEIPOT24__SOL",
        )
        evt1 = EventCompositeFactory(
            field=field1,
            geos=geos1,
            altitude=altitude,
            plain=Threshold(
                threshold=2.0, comparison_op=ComparisonOperator.SUPEGAL, units="cm"
            ),
            compute_list=["summary"],
        )
        evt2 = EventCompositeFactory(
            field=field1,
            geos=geos2,
            altitude=altitude,
            plain=Threshold(
                threshold=15, comparison_op=ComparisonOperator.SUPEGAL, units="mm"
            ),
            compute_list=["summary"],
        )
        evt3 = EventCompositeFactory(
            field=field2,
            geos=geos2,
            altitude=altitude,
            plain=Threshold(
                threshold=2.0, comparison_op=ComparisonOperator.SUPEGAL, units="cm"
            ),
            compute_list=["summary"],
        )

        lvl1 = LevelCompositeFactory(
            level=1,
            elements_event=[evt1, evt2],
            logical_op_list=["or"],
            aggregation_type=AggregationType.DOWN_STREAM,
            compute_list=["summary"],
            aggregation=AggregationFactory(),
        )
        lvl2 = LevelCompositeFactory(
            level=2,
            elements_event=[evt1, evt2],
            logical_op_list=["and"],
            aggregation_type=AggregationType.DOWN_STREAM,
            compute_list=["summary"],
            aggregation=AggregationFactory(),
        )
        lvl3 = LevelCompositeFactory(
            level=1,
            elements_event=[evt3],
            aggregation_type=AggregationType.DOWN_STREAM,
            compute_list=["summary"],
            aggregation=AggregationFactory(),
        )
        risk_compo = RiskComponentCompositeFactory(levels=[lvl1, lvl2, lvl3])

        risk_compo.compute()

        assert_equals_result(
            {
                "risks_ds": risk_compo.risks_ds.to_dict(),
                "final_risk_da": risk_compo.final_risk_da.to_dict(),
            }
        )

    def test_integration(self, assert_equals_result, root_path_cwd):
        data = JsonFile(self.inputs_dir / "small_conf_risk.json").load()
        data_prod = next(iter(data.values()))
        component = data_prod["components"][0]
        compo = RiskComponentComposite(**component)

        assert_equals_result(compo)

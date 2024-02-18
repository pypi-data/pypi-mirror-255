import datetime as dt
import shutil
from pathlib import Path

import numpy as np
import numpy.random as npr
import pytest

import mfire.utils.mfxarray as xr
from mfire.localisation import SpatialIngredient, SummarizedTable, TemporalLocalisation
from mfire.settings import SETTINGS_DIR
from mfire.utils import JsonFile, recursive_format
from mfire.utils.date import Datetime, Period, Timedelta
from tests.functions_test import assert_identically_close


class TestTemporalLocalisation:
    @pytest.mark.filterwarnings("ignore: invalid value")
    def test_temporal(self):
        # On fixe la seed afin d'avoir une reproductibilité des résultats.
        npr.seed(0)
        # Test fait sur 4 zones et 40 pas de temps
        din = xr.Dataset()
        din.coords["valid_time"] = [
            dt.datetime(2019, 1, 1) + dt.timedelta(hours=i) for i in range(40)
        ]
        din.coords["id"] = ["A" + str(i) for i in range(4)]
        din["elt"] = (("valid_time", "id"), npr.binomial(1, 0.1, (40, 4)))
        temp_loc = TemporalLocalisation(din["elt"])
        dout = temp_loc.new_division()

        expected_result = xr.Dataset()
        expected_result["period"] = [
            "20190101T02_to_20190101T06",
            "20190101T07_to_20190101T21",
            "20190101T22_to_20190102T13",
        ]
        expected_result["id"] = ["A0", "A1", "A2", "A3"]
        expected_result["elt"] = (
            ("period", "id"),
            [[1.0, 1.0, 0.0, 1.0], [1.0, 0.0, 1.0, 0.0], [0.0, 1.0, 1.0, 1.0]],
        )
        assert_identically_close(expected_result["elt"], dout)

        # On teste le fait de ne pas trimmer les périodes
        temp_loc.update(trim_period=False)
        dout = temp_loc.new_division()
        expected_result = xr.Dataset()
        expected_result["period"] = [
            "20190101T00_to_20190101T06",
            "20190101T07_to_20190101T21",
            "20190101T22_to_20190102T15",
        ]
        expected_result["id"] = ["A0", "A1", "A2", "A3"]
        expected_result["elt"] = (
            ("period", "id"),
            [[1.0, 1.0, 0.0, 1.0], [1.0, 0.0, 1.0, 0.0], [0.0, 1.0, 1.0, 1.0]],
        )
        assert_identically_close(expected_result["elt"], dout)

        # Test avec des données sur une période plus courte
        din = xr.Dataset()
        din.coords["valid_time"] = [
            dt.datetime(2019, 1, 1) + dt.timedelta(hours=i) for i in range(4)
        ]
        din.coords["id"] = ["A" + str(i) for i in range(2)]
        din["elt"] = (
            ("valid_time", "id"),
            [[True, True], [False, True], [True, True], [False, True]],
        )

        temp_loc = TemporalLocalisation(din["elt"])
        dout = temp_loc.new_division()
        expected_result = xr.Dataset()
        expected_result["period"] = ["20190101T00_to_20190101T03"]
        expected_result["id"] = ["A0", "A1"]
        expected_result["elt"] = (("period", "id"), [[1.0, 1]])

        assert_identically_close(expected_result["elt"], dout)

    def test_different_tempo(self):
        din = xr.Dataset()
        din.coords["valid_time"] = [
            dt.datetime(2019, 1, 1) + dt.timedelta(hours=i) for i in range(7)
        ]
        din.coords["id"] = ["A" + str(i) for i in range(2)]
        din["elt"] = (
            ("valid_time", "id"),
            [
                [False, True],
                [False, True],
                [False, True],
                [True, True],
                [True, True],
                [True, True],
                [True, True],
            ],
        )
        temp_loc = TemporalLocalisation(din["elt"])
        dout = temp_loc.new_division()

        expected_result = xr.Dataset()
        expected_result["period"] = [
            "20190101T00_to_20190101T02",
            "20190101T03_to_20190101T06",
        ]
        expected_result["id"] = ["A0", "A1"]
        expected_result["elt"] = (("period", "id"), [[0.0, 1], [1.0, 1.0]])
        assert_identically_close(expected_result["elt"], dout)
        dout = temp_loc.new_division(delta_h=2)
        expected_result = xr.Dataset()
        expected_result["period"] = [
            "20190101T00_to_20190101T02",
            "20190101T03_to_20190101T04",
            "20190101T05_to_20190101T06",
        ]
        expected_result["id"] = ["A0", "A1"]
        expected_result["elt"] = (("period", "id"), [[0.0, 1], [1.0, 1.0], [1.0, 1.0]])

        assert_identically_close(expected_result["elt"], dout)

    def test_large_tempo(self):
        din = xr.Dataset()
        din.coords["valid_time"] = [
            dt.datetime(2019, 1, 1) + dt.timedelta(hours=i) for i in range(12)
        ]
        din.coords["id"] = ["A" + str(i) for i in range(2)]
        din["elt"] = (
            ("valid_time", "id"),
            [
                [False, True],
                [False, True],
                [False, True],
                [False, True],
                [False, True],
                [True, True],
                [True, True],
                [True, True],
                [True, True],
                [False, True],
                [False, True],
                [False, True],
            ],
        )
        temp_loc = TemporalLocalisation(din["elt"])
        dout = temp_loc.new_division(delta_h=3)
        expected_result = xr.Dataset()
        expected_result["period"] = [
            "20190101T00_to_20190101T04",
            "20190101T05_to_20190101T08",
            "20190101T09_to_20190101T11",
        ]
        expected_result["id"] = ["A0", "A1"]
        expected_result["elt"] = (("period", "id"), [[0.0, 1], [1.0, 1.0], [0.0, 1.0]])
        assert_identically_close(expected_result["elt"], dout)

        dout = temp_loc.new_division(delta_h=5)
        expected_result = xr.Dataset()
        expected_result["period"] = [
            "20190101T00_to_20190101T04",
            "20190101T05_to_20190101T11",
        ]
        expected_result["id"] = ["A0", "A1"]
        expected_result["elt"] = (("period", "id"), [[0.0, 1], [1.0, 1.0]])
        assert_identically_close(expected_result["elt"], dout)

        # On teste le fait de ne pas trimmer les périodes
        temp_loc.update(trim_period=False)
        dout = temp_loc.new_division(delta_h=5)
        assert_identically_close(expected_result["elt"], dout)


def define_spatial_table(evt_size, risk_level=1):
    spatial_table = xr.Dataset()
    spatial_table.coords["id"] = [
        "CD38_domain_compass__Est",
        "CD38_domain_compass__NordOuest",
        "cde3bf79-4afd-43bb-88e7-7658c52f51b6",
    ]
    spatial_table.coords["risk_level"] = [risk_level]
    spatial_table.coords["evt"] = [i for i in range(0, evt_size)]
    spatial_table.coords["valid_time"] = [
        (Datetime(2020, 12, 8, 0) + Timedelta(hours=i)).as_np_dt64 for i in range(12)
    ]
    spatial_table["areaName"] = (("id"), ["Est", "NordOuest", "SudOuest"])
    spatial_table = spatial_table.swap_dims({"id": "areaName"}).swap_dims(
        {"areaName": "id"}
    )
    spatial_table["weatherVarName"] = (
        ("risk_level", "evt"),
        [["var_" + str(i) for i in range(0, evt_size)]],
    )
    dim_id = spatial_table.id.size
    dim_risk = spatial_table.risk_level.size
    dim_time = spatial_table.valid_time.size

    spatial_table["density"] = (
        ("risk_level", "evt", "valid_time", "id"),
        np.random.rand(dim_risk, evt_size, dim_time, dim_id),
    )
    spatial_table["rep_value_plain"] = (
        ("risk_level", "evt", "valid_time", "id"),
        4 + np.random.randn(dim_risk, evt_size, dim_time, dim_id),
    )
    spatial_table["risk_density"] = (
        ("risk_level", "valid_time", "id"),
        np.random.rand(dim_risk, dim_time, dim_id),
    )
    if evt_size == 1:
        spatial_table["risk_density"].values[0, 11, 1] = 0
    spatial_table["occurrence"] = spatial_table["risk_density"] > 0.6
    return spatial_table


def get_json_spatialIngredient(dirname: Path):
    dout = {
        "geos": {
            "file": dirname / "SpatialIngredient.nc",
            "grid_name": "eurw1s100",
            "domain_id": "CD38_domain",
            "full_list_id": [
                "CD38_domain_alt__sup_350",
                "CD38_domain_alt__sup_1200",
                "CD38_domain_alt__inf_500",
                "CD38_domain_alt__sup_800",
                "CD38_domain_compass__SudEst",
                "CD38_domain_alt__inf_300",
                "CD38_domain_alt__sup_700",
                "CD38_domain_alt__sup_1400",
                "CD38_domain_alt__inf_400",
                "CD38_domain_compass__SudOuest",
                "CD38_domain_alt__sup_600",
                "CD38_domain_compass__Nord",
                "CD38_domain_alt__sup_1000",
                "CD38_domain_alt__sup_300",
                "CD38_domain_alt__sup_1600",
                "CD38_domain_compass__Est",
                "CD38_domain_alt__sup_1800",
                "CD38_domain_compass__NordOuest",
                "CD38_domain_alt__sup_500",
                "CD38_domain_alt__sup_400",
                "CD38_domain_compass__Sud",
                "CD38_domain_alt__inf_250",
                "CD38_domain_compass__NordEst",
                "CD38_domain_alt__sup_900",
                "CD38_domain_compass__Ouest",
                "CD38_domain_alt__sup_250",
            ],
        },
        "localized": {
            "file": dirname / "SpatialIngredientlocalized.nc",
            "grid_name": "eurw1s100",
        },
    }
    return dout


class TestLocalisation:
    inputs_dir: Path = Path(__file__).parent / "inputs"

    def testTemporalDivision(self, tmp_path):
        np.random.seed(0)

        spatial_one = define_spatial_table(evt_size=1, risk_level=3)
        spatial_two = define_spatial_table(evt_size=3, risk_level=1)
        spatial_table = xr.merge([spatial_one, spatial_two])
        spatial_table.to_netcdf(tmp_path / "spatial_table.nc")

        JsonFile(tmp_path / "LocalisationInfo.json").dump(
            {
                "geo_id": "CD38_domain",
                "period": [
                    "2020-12-08T08:00:00.000000000",
                    "2020-12-08T09:00:00.000000000",
                ],
                "risk_level": 3,
            }
        )

        dictIngredient = get_json_spatialIngredient(tmp_path)
        JsonFile(tmp_path / "SpatialIngredient.json").dump(dictIngredient)
        shutil.copyfile(
            self.inputs_dir / "SpatialIngredient.nc",
            tmp_path / "SpatialIngredient.nc",
        )
        shutil.copyfile(
            self.inputs_dir / "SpatialIngredientlocalized.nc",
            tmp_path / "SpatialIngredientlocalized.nc",
        )

        JsonFile(tmp_path / "component.json").dump(
            recursive_format(
                JsonFile(self.inputs_dir / "component_config.json").load(),
                values={"settings_dir": SETTINGS_DIR},
            )
        )
        spatial_ingredient = SpatialIngredient.load(tmp_path / "SpatialIngredient")
        tempo_handler = TemporalLocalisation(
            spatial_table["occurrence"].isel(risk_level=1),
            area_dimension="id",
            time_dimension="valid_time",
        )
        table_3p = tempo_handler.new_division()
        da = xr.DataArray(
            [[0.0, 1.0, 0.0], [1.0, 1.0, 1.0], [1.0, 0.0, 1.0]],
            dims=("period", "id"),
            coords={
                "id": [
                    "CD38_domain_compass__Est",
                    "CD38_domain_compass__NordOuest",
                    "cde3bf79-4afd-43bb-88e7-7658c52f51b6",
                ],
                "period": [
                    "20201208T00_to_20201208T02",
                    "20201208T03_to_20201208T05",
                    "20201208T06_to_20201208T10",
                ],
                "risk_level": 3,
                "areaName": ("id", ["Est", "NordOuest", "SudOuest"]),
            },
            name="elt",
        )
        assert_identically_close(table_3p, da)

        period = Period(
            spatial_table.valid_time.min().values, spatial_table.valid_time.max().values
        )
        summarized_handler = SummarizedTable(
            table_3p,
            spatial_ingredient=spatial_ingredient,
            request_time=Datetime(2020, 12, 8, 0).strftime("%Y%m%dT%H"),
            full_period=period,
        )
        da = xr.DataArray(
            [[0.0, 1.0, 1.0], [1.0, 1.0, 0.0]],
            dims=("id", "period"),
            coords={
                "id": [
                    "CD38_domain_compass__Est_+_cde3bf79-4afd-43bb-88e7-7658c52f51b6",
                    "CD38_domain_compass__NordOuest",
                ],
                "period": [
                    "20201208T00_to_20201208T02",
                    "20201208T03_to_20201208T05",
                    "20201208T06_to_20201208T10",
                ],
                "risk_level": 3,
                "areaName": ("id", ["Est_+_SudOuest", "NordOuest"]),
                "areaType": ("id", ["mergedArea", ""]),
            },
            name="elt",
        )
        fname = tmp_path / "tmp.nc"
        da.to_netcdf(fname)
        db = xr.open_dataarray(fname)
        db = db.drop_vars(["areaName", "areaType"])
        unique_table = summarized_handler.unique_table.drop_vars(
            ["areaName", "areaType"]
        )
        assert_identically_close(db, unique_table)

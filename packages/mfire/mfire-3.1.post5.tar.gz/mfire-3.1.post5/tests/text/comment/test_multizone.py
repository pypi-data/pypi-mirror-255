import shutil
from pathlib import Path

import numpy as np
import pytest

import mfire.utils.mfxarray as xr
from mfire.localisation import Localisation
from mfire.settings import SETTINGS_DIR
from mfire.text.comment.multizone import ComponentHandlerLocalisation
from mfire.utils import JsonFile, recursive_format
from mfire.utils.date import Datetime, Timedelta


# On doit créer le tableau spatial
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


class TestComponentHandlerLocalisation:
    inputs_dir: Path = Path(__file__).parent / "inputs"

    def _copy_data(self, path):
        spatial_one = define_spatial_table(evt_size=1, risk_level=3)
        spatial_two = define_spatial_table(evt_size=3, risk_level=1)
        spatial_table = xr.merge([spatial_one, spatial_two])
        spatial_table.to_netcdf(path / "spatial_table.nc")

        JsonFile(path / "LocalisationInfo.json").dump(
            {
                "geo_id": "CD38_domain",
                "period": [
                    "2020-12-08T08:00:00.000000000",
                    "2020-12-08T09:00:00.000000000",
                ],
                "risk_level": 3,
            }
        )

        dictIngredient = get_json_spatialIngredient(path)
        JsonFile(path / "SpatialIngredient.json").dump(dictIngredient)
        shutil.copyfile(
            self.inputs_dir / "SpatialIngredient.nc",
            path / "SpatialIngredient.nc",
        )
        shutil.copyfile(
            self.inputs_dir / "SpatialIngredientlocalized.nc",
            path / "SpatialIngredientlocalized.nc",
        )

        JsonFile(path / "component.json").dump(
            recursive_format(
                JsonFile(self.inputs_dir / "component_config.json").load(),
                values={"settings_dir": SETTINGS_DIR},
            )
        )

    @pytest.mark.skip
    def testA(self, tmp_path):
        self._copy_data(tmp_path)

        loca_handler = Localisation.load(repo=tmp_path)
        component = ComponentHandlerLocalisation(loca_handler)
        assert "P3_3_6" == component.get_template_key()
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
        )
        fname = tmp_path / "tmp.nc"
        da.to_netcdf(fname)
        db = xr.open_dataarray(fname)
        db = db.drop_vars(["areaName", "areaType"])
        unique_table = component.get_unique_table().drop_vars(["areaName", "areaType"])
        xr.testing.assert_equal(db, unique_table)

        # On va aussi tester les valeurs critiques
        critical_values = component.get_critical_value()
        assert critical_values == {
            "var_0": {
                "mountain_altitude": 1000,
                "plain": {
                    "critical_hour": np.datetime64("2020-12-08T05:00:00.000000000"),
                    "id": "CD38_domain_compass__Est",
                    "next_critical": None,
                    "operator": "sup",
                    "units": None,
                    "value": 5.95077539523179,
                    "threshold": 3,
                },
            }
        }

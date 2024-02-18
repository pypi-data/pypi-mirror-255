import os.path
from pathlib import Path
from unittest import mock

from mfire.composite.geos import AltitudeComposite
from mfire.configuration.component_base import CompoBase
from mfire.configuration.datas import RHManager
from mfire.configuration.levels import EventManager, LevelManager
from mfire.configuration.rules import Rules
from mfire.settings import Settings
from mfire.utils.date import Datetime

# Basic tests configuration


class Test_LevelManager:
    """New class for testing the config composite step"""

    def get_settings_mock(
        self,
    ):
        settings = Settings()
        settings.altitudes_dirname = "mfire/settings/geos/altitudes/"
        settings.data_config_filename = "configs/data_task_config.json"
        settings.data_dirname = Path("data")
        return settings

    def test_init(self, assert_equals_result, root_path_cwd):
        with mock.patch.object(RHManager, "get_settings", new=self.get_settings_mock):
            # on mémorise juste les varaibles
            result = LevelManager(
                compobase=None,
                rhmanager=None,
                compo_config=None,
                geos_base=None,
                box=((0, 0), (1, 1)),
                file_id="",
                start_stop=[Datetime("20230824"), Datetime("20230825")],
            )
            assert_equals_result(result)

    def test_get_new_level(self):
        assert True


class Test_EventManager:
    def get_settings_mock(
        self,
    ):
        settings = Settings()
        settings.altitudes_dirname = "mfire/settings/geos/altitudes/"
        settings.data_config_filename = "configs/data_task_config.json"
        settings.data_dirname = Path("data")
        return settings

    def get_event(
        self,
    ):
        day = "2023-08-24T00:00:00+00:00"
        tday = "20230824T0000"
        hour = 12
        thour = "12"
        file_id = "france_jj1_" + day + "_maj" + str(hour)
        dataconfig = {
            (file_id, "EAU24__SOL"): [
                {
                    "kind": "promethee_gridpoint",
                    "model": "promethee",
                    "date": day,
                    "geometry": "eurw1s100",
                    "cutoff": "production",
                    "origin": "production",
                    "nativefmt": "netcdf",
                    "vapp": "promethee",
                    "vconf": "msb",
                    "experiment": "TEST",
                    "block": "MAJ" + thour,
                    "namespace": "vortex.cache.fr",
                    "format": "grib",
                    "param": "EAU24__SOL",
                    "begintime": hour,
                    "endtime": 48,
                    "step": 1,
                    "local": "data/"
                    + tday
                    + "/promethee/EURW1S100/EAU24__SOL.00"
                    + thour
                    + "_0048_0001.netcdf",
                    "role": file_id + " EAU24__SOL",
                    "fatal": False,
                    "now": True,
                }
            ]
        }
        compobase = CompoBase(
            single_data_config=dataconfig,
            single_mask_config=None,
            processed_periods=None,
            processed_hazards=None,
            all_shapes=[],
        )
        compo_config = {
            "alt_min": -100,
            "alt_max": 2000,
        }
        rules = Rules(
            name="alpha",
            drafting_datetime=Datetime("20230824T12:00:00+00:00"),
            dirname="mfire/settings/rules/",
        )
        with mock.patch.object(RHManager, "get_settings", new=self.get_settings_mock):
            rhmanager = RHManager(rules=rules)
            levelmanager = LevelManager(
                compobase=compobase,
                rhmanager=rhmanager,
                compo_config=compo_config,
                geos_base={"file": ""},
                box=((0, 0), (1, 1)),
                file_id=file_id,
                start_stop=[Datetime("20230824"), Datetime("20230825")],
            )
            aggreg = {"kwargs": {"dr": "5"}, "method": "requiredDensity"}
            return EventManager(levelmanager=levelmanager, aggregation_aval=aggreg)

    def test_init(
        self,
        root_path_cwd,
        assert_equals_result,
    ):
        result = self.get_event()
        level_compo = result.levelmanager
        compobase = level_compo.compobase
        data_config = compobase.single_data_config
        data_config = {str(key): val for key, val in data_config.items()}
        compobase.single_data_config = data_config
        assert_equals_result(compobase)

    def test_get_new_event(
        self,
        assert_equals_result,
        root_path_cwd,
    ):
        eventmanager = self.get_event()
        event = {
            "field": "EAU24__SOL",
            "category": "quantitative",
            "plain": {"threshold": 30, "comparisonOp": "supegal", "units": "mm"},
        }
        with mock.patch.object(RHManager, "get_settings", new=self.get_settings_mock):
            result = eventmanager.get_new_event(event)
            basename = os.path.basename(result.altitude.filename)
            filename = "mfire/settings/geos/altitudes/" + basename
            result.altitude = AltitudeComposite(
                filename=filename,
                alt_min=result.altitude.alt_min,
                alt_max=result.altitude.alt_max,
            )
            assert_equals_result(result)

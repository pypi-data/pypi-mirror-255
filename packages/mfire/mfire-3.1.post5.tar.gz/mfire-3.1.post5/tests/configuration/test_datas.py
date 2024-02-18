from pathlib import Path
from unittest import mock

from mfire.configuration.datas import RHManager
from mfire.configuration.rules import Rules
from mfire.settings import Settings
from mfire.utils.date import Datetime

# Basic tests configuration
DRAFTING_DATETIME = Datetime(2022, 1, 1, 8, 31, 12)


class Test_RHManager:
    settings = None
    rules = Rules(name="alpha", drafting_datetime=DRAFTING_DATETIME)
    """New class for testing the config composite step"""

    def get_settings_mock(
        self,
    ):
        settings = Settings()
        settings.altitudes_dirname = "mfire/settings/geos/altitudes/"
        settings.data_config_filename = "configs/data_task_config.json"
        settings.data_dirname = Path("data")

        return settings

    def test_init(self):
        # on mémorise juste les varaibles
        result = RHManager(settings=self.settings, rules=self.rules)
        assert result

    def test_create_rh(self, assert_equals_result):
        with mock.patch.object(RHManager, "get_settings", new=self.get_settings_mock):
            rhmanager = RHManager(rules=self.rules)
            run_day = DRAFTING_DATETIME.replace(hour=0, minute=0, second=0)
            day = run_day.isoformat()
            file_id = "pprod_frjj1_" + day + "_maj" + str(DRAFTING_DATETIME.hour)
            result = rhmanager.create_rh(file_id, DRAFTING_DATETIME, "RAF")
            assert_equals_result(result)

    def test_create_full_file_config(self, assert_equals_result):
        with mock.patch.object(RHManager, "get_settings", new=self.get_settings_mock):
            run_day = DRAFTING_DATETIME.replace(hour=0, minute=0, second=0)
            day = run_day.isoformat()
            file_id = "pprod_frjj1_" + day + "_maj" + str(DRAFTING_DATETIME.hour)
            rhmanager = RHManager(settings=self.settings, rules=self.rules)
            result = rhmanager.create_full_file_config(
                file_id, DRAFTING_DATETIME, "RAF"
            )
            assert_equals_result(result)

    def test_preprocessed_rh(self, assert_equals_result):
        with mock.patch.object(RHManager, "get_settings", new=self.get_settings_mock):
            run_day = DRAFTING_DATETIME.replace(hour=0, minute=0, second=0)
            day = run_day.isoformat()
            file_id = "pprod_frjj1_" + day + "_maj" + str(DRAFTING_DATETIME.hour)
            rhmanager = RHManager(settings=self.settings, rules=self.rules)
            result = rhmanager.create_full_file_config(
                file_id, DRAFTING_DATETIME, "RAF__HAUTEUR10"
            )
            assert_equals_result(result)

    def test_source_files_terms(self, assert_equals_result):
        with mock.patch.object(RHManager, "get_settings", new=self.get_settings_mock):
            run_day = DRAFTING_DATETIME.replace(hour=0, minute=0, second=0)
            day = run_day.isoformat()
            hour = DRAFTING_DATETIME.strftime("%H")
            file_id = "france_jj1_" + day + "_maj" + hour
            rhmanager = RHManager(settings=self.settings, rules=self.rules)
            data_config = {
                "config_version": "04801c74",
                "sources": {},
                "preprocessed": {},
            }
            result = rhmanager.source_files_terms(
                data_config, file_id, "RAF__HAUTEUR10", None
            )
            assert_equals_result(result)

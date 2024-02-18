from pathlib import Path
from typing import Optional
from unittest import mock

import numpy as np

from mfire.composite.geos import AltitudeComposite
from mfire.configuration import VersionConfig
from mfire.configuration.config_metronome_processor import ConfigMetronomeProcessor
from mfire.configuration.config_tools import config_metronome
from mfire.configuration.configs import ConfigGlobal
from mfire.configuration.datas import RHManager
from mfire.settings import get_logger
from mfire.utils.date import Datetime

# Logging
LOGGER = get_logger(name="config_processor.mod", bind="testconfig_processor")

# numpy.random seed
np.random.seed(42)

# Basic tests configuration
DRAFTING_DATETIME = Datetime(2021, 10, 20, 8)


class TestConfigMetronomeProcessor:
    """New class for testing the config processing step"""

    inputs_dir: Path = Path(__file__).parent / "inputs"

    config_basename: Path = Path("prometheeInit.json")

    def grid_name_mock(
        self,
        grid_name: str,
        alt_min: Optional[int] = None,
        alt_max: Optional[int] = None,
    ):
        return AltitudeComposite(
            filename=f"mfire/settings/geos/altitudes/{grid_name}.nc",
            alt_min=alt_min,
            alt_max=alt_max,
        )

    def single_config_test(self, rules: str):
        config_filename = self.inputs_dir / self.config_basename
        cp = ConfigMetronomeProcessor(
            config_filename=config_filename,
            rules=rules,
            drafting_datetime=DRAFTING_DATETIME,
            experiment="TEST",
        )
        configs = config_metronome(config_filename)
        cp.set_confhash(configs)
        cp.set_configuration_datetime(configs)
        config_global = ConfigGlobal(
            cp.experiment,
            cp.hashcode,
            cp.settings,
            cp.rules,
            cp.get_geo,
            cp.list_components_configs,
        )

        mask_dico, data_dico, prod_dico, _, _ = cp.process_single_prod(
            config_global, configs[0]
        )

        data_dico = {" ".join(key): value for key, value in data_dico.items()}
        data_sort = {key: data_dico[key] for key in sorted(data_dico.keys())}
        prod_dico["components"] = sorted(
            prod_dico["components"], key=lambda k: (k["id"], k["hazard_id"])
        )
        return {"mask": mask_dico, "data": data_sort, "prod": prod_dico}

    def test_single_config_alpha(self, assert_equals_result, root_path_cwd):
        with mock.patch.object(
            AltitudeComposite, "from_grid_name", new=self.grid_name_mock
        ):
            result = self.single_config_test(rules="alpha")
            assert_equals_result(result)

    def test_single_config_psym(self, assert_equals_result, root_path_cwd):
        with mock.patch.object(
            AltitudeComposite, "from_grid_name", new=self.grid_name_mock
        ):
            result = self.single_config_test(rules="psym")
            assert_equals_result(result)

    def test_single_config_psym_archive(self, assert_equals_result, root_path_cwd):
        with mock.patch.object(
            AltitudeComposite, "from_grid_name", new=self.grid_name_mock
        ):
            result = self.single_config_test(rules="psym_archive")
            assert_equals_result(result)

    def test_source_file_terms(
        self,
        assert_equals_result,
    ):
        config_filename = self.inputs_dir / self.config_basename
        cp = ConfigMetronomeProcessor(
            config_filename=config_filename,
            rules="alpha",
            drafting_datetime=DRAFTING_DATETIME,
            experiment="TEST",
        )
        configs = config_metronome(config_filename)
        cp.set_confhash(configs)
        cp.set_configuration_datetime(configs)

        assert cp.version_config == VersionConfig(
            version="909d189f",
            drafting_datetime=Datetime(2021, 10, 20, 8),
            reference_datetime=Datetime(2021, 10, 20, 8),
            production_datetime=Datetime(2021, 10, 20, 9),
            configuration_datetime=Datetime(2021, 10, 19, 20, 45, 12),
        )
        rhmanager = RHManager(settings=cp.settings, rules=cp.rules)
        data_config = {
            "config_version": cp.hashcode,
            "sources": dict(),
            "preprocessed": dict(),
        }
        assert_equals_result(data_config)

        source_terms_dico = rhmanager.source_files_terms(
            data_config=data_config,
            file_id="france_jj1_2021-10-20T00:00:00+00:00_maj08",
            param="FF__HAUTEUR10",
            accum=None,
        )
        sources_terms_ref = {
            "pprod_frjj1_2021-10-20T00:00:00+00:00_maj8": {
                "terms": list(range(8, 49)),
                "step": 1,
            }
        }
        assert source_terms_dico == sources_terms_ref

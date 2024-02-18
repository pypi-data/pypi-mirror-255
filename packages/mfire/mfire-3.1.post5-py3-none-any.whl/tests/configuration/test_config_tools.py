import tarfile
from pathlib import Path

import pandas as pd
import pytest

from mfire.configuration.config_tools import (
    BoundingBox,
    base_component_config,
    config_metronome,
    reshape_hazard,
    reshape_risk_component,
    reshape_text_component,
)
from mfire.configuration.geos import FeatureCollectionConfig
from mfire.utils import JsonFile


class Test_config_tools:
    """New class for testing the config processing step"""

    inputs_dir: Path = Path(__file__).parent / "inputs"
    config_basename: Path = Path("config_tools.json")
    base_config = JsonFile(inputs_dir / config_basename).load()

    @pytest.fixture(scope="session")
    def local_working_dir(self, working_dir) -> Path:
        """pytest fixture for creating a new tmp working directory"""
        return working_dir

    def test_config_metronome(self, local_working_dir: Path):
        dirname = local_working_dir
        dico = {"3": 4}
        filename = dirname / "1.json"
        JsonFile(str(filename)).dump(dico)
        assert [{"3": 4}] == config_metronome(filename)
        dicp = {"1": 2}
        filenamf = dirname / "2.json"
        JsonFile(str(filenamf)).dump(dicp)
        assert [{"1": 2}] == config_metronome(filenamf)
        filenamg = dirname / "12.tgz"
        archive = tarfile.open(filenamg, "w:gz")
        archive.add(filename)
        archive.add(filenamf)
        archive.close()
        assert [{"3": 4}, {"1": 2}] == config_metronome(filenamg)

    def test_base_component_config(self, assert_equals_result):
        output = base_component_config(self.base_config[0]["components"][0])
        assert_equals_result(output)

    def test_reshape_hazard(self, assert_equals_result):
        component_df = pd.DataFrame(
            [
                [
                    "89a5cae9-731c-4b79-be68-b8a92978e6b0",
                    "751410a0-a404-45de-8548-1944af4c6e60",
                    "Vent",
                    "da21482f-f56e-4088-b5e9-3200ff5cfa9a",
                    0,
                    0,
                    0,
                ]
            ],
            columns=[
                "hazard_id",
                "period",
                "hazard_name",
                "geo",
                "hazard_idx",
                "level_idx",
                "config_idx",
            ],
        )

        # je n'ai pas réussi à créer le dataframe component_df pour
        # qu'il soit égal au résultat
        # par contre en les exportant comme dico : ils sont bien égaux
        resultat = reshape_hazard(
            0,
            self.base_config[0]["components"][0]["data"]["hazards"][0],
            component_df.columns,
        ).to_dict()
        assert_equals_result(resultat)

    def test_reshape_risk_component(self, assert_equals_result):
        result_compo = reshape_risk_component(self.base_config[0]["components"][0])
        assert_equals_result(result_compo)

    def test_reshape_text_component(self, assert_equals_result):
        result_compo = reshape_text_component(self.base_config[0]["components"][1])
        assert_equals_result(result_compo)

    def test_get_box_geos(self):
        ref_compo = ((46.0, 45.0), (4.0, 5.0))
        all_geos = FeatureCollectionConfig(features=self.base_config[0]["geos"])
        compo = reshape_risk_component(self.base_config[0]["components"][0])[0]
        bounding = BoundingBox(all_geos)
        result_compo = bounding.get_box_geos(compo)
        assert result_compo == ref_compo

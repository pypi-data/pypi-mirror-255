from pathlib import Path

from mfire.configuration.component_base import CompoBase, ComponentManager
from mfire.configuration.datas import RHManager
from mfire.configuration.geos import FeatureCollectionConfig
from mfire.configuration.rules import Rules
from mfire.settings import Settings
from mfire.utils.date import Datetime
from mfire.utils.json_utils import JsonFile

# Basic tests configuration
DRAFTING_DATETIME = Datetime(2021, 10, 20, 8)


class Test_compobase:
    """New class for testing the config processing step"""

    def test_init(self, assert_equals_result):
        compo = CompoBase()
        assert_equals_result(compo)


class Test_ComponentManager:

    inputs_dir: Path = Path(__file__).parent / "inputs"

    config_basename: Path = Path("components.json")

    base_config = [
        {
            "geos": [
                {
                    "id": "eur",
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [4, 46],
                                [5, 46],
                                [5, 45],
                                [4, 45],
                                [4, 46],
                            ]
                        ],
                    },
                },
                {
                    "id": "global",
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [150, -43],
                                [170, -43],
                                [170, -44],
                                [150, -44],
                                [150, -43],
                            ]
                        ],
                    },
                },
            ]
        }
    ]

    def test_useablegeometries(self, assert_equals_result):
        config_filename = self.inputs_dir / self.config_basename
        base_config = JsonFile(config_filename).load()
        rules = Rules(name="alpha", drafting_datetime=DRAFTING_DATETIME)
        config_datetime = DRAFTING_DATETIME
        rhmanager = RHManager(settings=Settings(), rules=rules)
        compomanager = ComponentManager(rhmanager, config_datetime)
        assert [] == compomanager.useable_geometries({})
        all_geos = FeatureCollectionConfig(features=base_config[0]["geos"])
        result = (
            compomanager.useable_geometries(all_geos[0].shape),
            compomanager.useable_geometries(all_geos[1].shape),
        )
        assert_equals_result(result)

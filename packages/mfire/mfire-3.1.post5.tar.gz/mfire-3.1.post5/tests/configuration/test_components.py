from pathlib import Path

import pytest

from mfire.composite import RiskComponentComposite, TextComponentComposite
from mfire.configuration.component_base import CompoBase, ComponentManager
from mfire.configuration.components import ComponentFactory
from mfire.configuration.config_tools import (
    BoundingBox,
    reshape_risk_component,
    reshape_text_component,
)
from mfire.configuration.datas import RHManager
from mfire.configuration.geos import FeatureCollectionConfig, MaskConfig
from mfire.configuration.periods import PeriodCollectionConfig
from mfire.configuration.resources import MaskRHConfig
from mfire.configuration.rules import Rules
from mfire.settings import Settings
from mfire.utils.date import Datetime
from mfire.utils.exception import ConfigurationError
from mfire.utils.json_utils import JsonFile

# Basic tests configuration
DRAFTING_DATETIME = Datetime(2021, 10, 20, 7)
BULLETIN_DATETIME = Datetime(2021, 10, 20, 10)


class Test_componentfactory:
    """New class for testing the config processing step"""

    inputs_dir: Path = Path(__file__).parent / "inputs"

    config_basename: Path = Path("components.json")

    def test_getComponent(self):
        with pytest.raises(ConfigurationError):
            config = {}
            ComponentFactory.getComponent(None, None, None, config)
        with pytest.raises(ConfigurationError):
            config = {"type": "autre"}
            ComponentFactory.getComponent(None, None, None, config)
        config_filename = self.inputs_dir / self.config_basename
        base_config = JsonFile(config_filename).load()
        all_geos = FeatureCollectionConfig(features=base_config[0]["geos"])
        bounding = BoundingBox(all_geos)
        risks = reshape_risk_component(base_config[0]["components"][0])
        texts = reshape_text_component(base_config[0]["components"][1])
        rules = Rules(name="alpha", drafting_datetime=DRAFTING_DATETIME)
        config_datetime = DRAFTING_DATETIME
        settings = Settings()
        rhmanager = RHManager(settings=settings, rules=rules)
        compomanager = ComponentManager(rhmanager, config_datetime)
        data = {}
        mask = MaskConfig(
            file="mask.nc",
            id="prod_id",
            name="Test Component",
            config_hash="neserta rien",
            prod_hash="idem",
            geos=FeatureCollectionConfig(features=base_config[0]["geos"]),
            resource_handler=MaskRHConfig(
                role="mask_prod_id",
                fatal=False,
                kind="promethee_mask",
                promid="prod_id",
                version=None,  # automatically changed by the validator
                namespace="vortex.cache.fr",
                experiment=settings.experiment,
                vapp=settings.vapp,
                vconf=settings.vconf,
                block="masks",
                format="netcdf",
                local="mask_file",
            ),
        )

        period = PeriodCollectionConfig(**base_config[0]).get_processed_periods(
            production_datetime=BULLETIN_DATETIME
        )
        hazard = {
            "89a5cae9-731c-4b79-be68-b8a92978e6b0": base_config[0]["components"][0][
                "data"
            ]["hazards"][0]
        }
        shape = {
            geo.id: geo.shape
            for geo in FeatureCollectionConfig(features=base_config[0]["geos"])
        }
        print(period)
        compobase = CompoBase(
            single_data_config=data,
            single_mask_config=mask,
            processed_periods=period,
            processed_hazards=hazard,
            all_shapes=shape,
        )

        compo = ComponentFactory.getComponent(
            compomanager, compobase, bounding, risks[0]
        )
        assert isinstance(compo[0], RiskComponentComposite)
        compo = ComponentFactory.getComponent(
            compomanager, compobase, bounding, texts[0]
        )
        assert isinstance(compo[0], TextComponentComposite)

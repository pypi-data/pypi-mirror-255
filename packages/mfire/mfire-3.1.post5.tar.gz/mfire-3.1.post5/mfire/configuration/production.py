"""
@package configuration.production

Porduction for Config processor module
"""

# Standard packages
from copy import deepcopy

from mfire.configuration.component_base import CompoBase, ComponentManager
from mfire.configuration.components import ComponentFactory
from mfire.configuration.config_tools import BoundingBox
from mfire.configuration.datas import RHManager

# local package
from mfire.configuration.geos import MaskConfig
from mfire.configuration.periods import PeriodCollectionConfig
from mfire.configuration.resources import MaskRHConfig

# Own package
from mfire.settings import get_logger
from mfire.utils import MD5
from mfire.utils.date import Datetime
from mfire.utils.exception import ConfigurationError
from mfire.utils.json_utils import prepare_json

# Third parties packages


# Logging
LOGGER = get_logger(name="config_processor.mod", bind="config_processor")


class Production:
    def __init__(
        self,
        config_global,
        config_prod,
    ):
        self.config_global = config_global
        self.prod = config_prod
        self.rhmanager = RHManager(
            settings=config_global.settings, rules=config_global.rules
        )
        self.compomanager = ComponentManager(
            self.rhmanager, self.configuration_datetime
        )
        self.shapes = {}

    @property
    def prod_hashcode(self):
        return MD5(self.prod).hash

    @property
    def prod_id(self):
        return self.prod.get("production_id", 0)

    @property
    def prod_name(self):
        return self.prod.get("production_name", f"production_{self.prod_id}")

    @property
    def configuration_datetime(self):
        return Datetime(self.prod.get("date_config"))

    def single_mask_config(self, settings):
        mask_file = settings.mask_dirname / f"{self.prod_id}.nc"
        single_mask_config = MaskConfig(
            file=mask_file,
            id=self.prod_id,
            name=self.prod_name,
            config_hash=self.config_global.config_hash,
            prod_hash=self.prod_hashcode,
            geos=self.config_global.get_geo(self.prod["geos"]),
            resource_handler=MaskRHConfig(
                role=f"mask_{self.prod_id}",
                fatal=False,
                kind="promethee_mask",
                promid=self.prod_id,
                version=None,  # automatically changed by the validator
                namespace="vortex.cache.fr",
                experiment=settings.experiment,
                vapp=settings.vapp,
                vconf=settings.vconf,
                block="masks",
                format="netcdf",
                local=mask_file,
            ),
        )
        return single_mask_config

    def processed_periods(self, bulletin_datetime):
        # Processing periods
        return PeriodCollectionConfig(**self.prod).get_processed_periods(
            production_datetime=bulletin_datetime
        )

    def processed_hazards(
        self,
    ):
        processed_hazards = dict()
        global LOGGER
        for hazard in self.prod["hazards"]:
            LOGGER = LOGGER.bind(hazard_id=hazard["id"])
            if isinstance(hazard["id"], (list, tuple)):
                LOGGER.warning(
                    "Given hazard['id'] as list (or tuple)",
                    func="process_single_prod",
                )
                if len(hazard["id"]) > 1:
                    raise ConfigurationError(
                        "Given hazard['id'] as list or tuple,"
                        f"of length {len(hazard['id'])} > 1",
                        func="process_single_prod",
                    )
                hazard["id"] = hazard["id"][0]
            processed_hazards[hazard["id"]] = deepcopy(hazard)
        LOGGER = LOGGER.try_unbind("hazard_id")
        return processed_hazards

    def get_shapes(self, geos):
        if len(self.shapes) == 0:
            self.shapes = {geo.id: geo.shape for geo in geos}
        return self.shapes

    def single_config(self):
        global LOGGER
        single_prod_config = {
            "id": self.prod_id,
            "name": self.prod_name,
            "config_hash": self.config_global.config_hash,
            "prod_hash": self.prod_hashcode,
            "mask_hash": None,
            "components": [],
        }
        # Processing periods
        processed_periods = self.processed_periods(
            self.config_global.rules.bulletin_datetime
        )
        LOGGER.info("Periods created,", func="process_single_prod")
        # Processing Hazards
        processed_hazards = self.processed_hazards()
        LOGGER.info("Hazards created,", func="process_single_prod")
        single_mask_config = self.single_mask_config(self.config_global.settings)
        single_prod_config["mask_hash"] = single_mask_config.mask_hash
        single_data_config = dict()
        components_configs = self.config_global.list_components_configs(self.prod)
        nb_compos = len(components_configs)
        all_geos = self.config_global.get_geo(self.prod["geos"])
        all_shapes = self.get_shapes(all_geos)
        bounding = BoundingBox(all_geos)
        compobase = CompoBase(
            single_data_config=single_data_config,
            single_mask_config=single_mask_config,
            processed_periods=processed_periods,
            processed_hazards=processed_hazards,
            all_shapes=all_shapes,
        )
        [
            single_prod_config["components"].extend(
                ComponentFactory.getComponent(
                    self.compomanager, compobase, bounding, compo_config
                )
            )
            for compo_config in components_configs
        ]
        compo_ok = len(single_prod_config["components"])
        if compo_ok == 0:
            raise ConfigurationError(f"No component to perform on {nb_compos} config")
        report_error_component = nb_compos - compo_ok
        # decode from complex object and encode to standard python object
        # due to issue with parallelism and complex object in callback transition
        single_prod_config = prepare_json(single_prod_config)
        return (
            single_mask_config,
            single_data_config,
            single_prod_config,
            compo_ok,
            report_error_component,
        )

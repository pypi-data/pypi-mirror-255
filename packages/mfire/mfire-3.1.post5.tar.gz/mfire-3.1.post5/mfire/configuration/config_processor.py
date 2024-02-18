"""
@package configuration.config_processor

Config processor module
"""

from importlib import import_module

# Standard packages
from os import cpu_count, getpid
from pathlib import Path
from time import time
from typing import Dict, Tuple

from mfire.configuration.config_tools import config_metronome

# local package
from mfire.configuration.configs import ConfigGlobal, VersionConfig
from mfire.configuration.datas import RHManager
from mfire.configuration.geos import FeatureCollectionConfig, MaskConfig
from mfire.configuration.rules import Rules

# Own package
from mfire.settings import Settings, get_logger
from mfire.utils import MD5, JsonFile, Parallel
from mfire.utils.date import Datetime

# Third parties packages


# Logging
LOGGER = get_logger(name="config_processor.mod", bind="config_processor")


# Main class : ConfigProcessor
class ConfigProcessor:
    """ConfigProcessor : Parses a configuration file (tar archive or json)
    and produces three configurations files out of it :

    * a mask configuration (self.mask_config): config following the geojson
    standard which describes all the geographical geos used in production.
    This file is to be used by the mask creation module.

    * a data configuration (self.data_config) : config which describes all
    the raw data files (using the Vortex Standard) necessary for production
    and all the pre-processings that must be done before production (parameter
    extraction, accumulations, combinations, etc.)
    This file is to be used by the data preprocessing module.

    * a production configuration (self.prod_config) : config which describes
    all the files necessary for production and all the processing to be done
    in order to produce Promethee data (risks and texts).
    This file is to be used by the core module.
    """

    def __init__(
        self,
        config_filename: Path,
        rules: str,
        drafting_datetime: Datetime,
        experiment: str,
    ):
        """__init__

        Args:
            config_filename (Path): path to the configuration file to process
            rules (str): Name of the rules convention used for files selection. This
                argument must belong to the RULES_NAMES list.
            drafting_datetime (datetime.datetime): Promethee's drafting datetime
        """
        LOGGER.info("Trying to set experiment... ", func="__init__")
        if isinstance(experiment, str):
            self.experiment = experiment.upper()
        else:
            self.experiment = None
        LOGGER.info(f"experiment set to {self.experiment}.", func="__init__")

        LOGGER.info("Setting the configuration file... ", func="__init__")
        config_filename = Path(config_filename)
        self.settings = Settings(config_filename=config_filename)
        LOGGER.info(
            f"configuration file set to {self.settings.config_filename}",
            func="__init__",
        )

        LOGGER.info("Initiating rules... ", func="__init__")
        self.rules = Rules(name=rules, drafting_datetime=drafting_datetime)
        LOGGER.info("Rules validated.", func="__init__")

    def set_confhash(self, configs):
        self.confhash = MD5(configs).hash

    @property
    def hashcode(self) -> str:
        """hashcode

        Returns:
            str : hexadecimal hash key of the config's MD5 checksum
        """
        return self.confhash

    def set_configuration_datetime(self, configs):
        self.configuration_datetime = Datetime(configs[0].get("date_config"))

    def get_configuration_datetime(self):
        return self.configuration_datetime

    @staticmethod
    def list_components_configs(single_config):
        """list_components_config : list all the components configurations
        contained in a prod_idx configuration.

        Args:
            prod_idx (int): Production index in the self.config
        """
        return single_config["components"]

    @staticmethod
    def get_geo(config: dict) -> FeatureCollectionConfig:
        """Patch to transform config geos config such as it is compatible
        with GeoJSON format

        Args:
            config (dict): geo configs

        Returns:
            FeatureCollection: Corresponding feature collection
        """
        return FeatureCollectionConfig(**config)

    def process_single_prod(
        self, config_global, single_config
    ) -> Tuple[MaskConfig, Dict, Dict]:
        """process_single_prod

        Args:
            production (dict): configuration of a single bulletin

        Returns:
            (MaskConfig, dict, dict): Tuple containing :
                * the extracted mask configuration MaskConfig (geoJSON standard)
                * the dict of all the data_files (filename and params) necessary
                for production
                * the extracted production configuration dictionary
        """
        global LOGGER
        LOGGER.info(
            f"Configuration start {single_config['production_id']}",
            func="process_single_prod",
        )
        t0 = time()
        production_module = import_module("mfire.configuration.production")
        production = production_module.Production(config_global, single_config)
        LOGGER = LOGGER.bind(prod_id=production.prod_id)
        (
            single_mask_config,
            single_data_config,
            single_prod_config,
            compo_ok,
            error_components,
        ) = production.single_config()
        LOGGER.info(
            f"Configuration ended {single_config['production_id']}. "
            f"({error_components} errors on components",
            func="process_single_prod",
            elapsed_time=time() - t0,
        )
        LOGGER = LOGGER.try_unbind(
            "prod_id",
            "compo_id",
            "period_id",
            "mask_id",
            "param",
            "level",
            "file_id",
        )

        return (
            single_mask_config,
            single_data_config,
            single_prod_config,
            compo_ok,
            error_components,
        )

    def append_config(self, single_processed_configs):
        """append_config : callback method for parallel processing
        of individual processed configs

        Args:
            single_processed_configs ([type]): [description]
        """
        t0 = time()
        prod_id = single_processed_configs[0].id
        LOGGER.debug("Receiving processed config.", prod_id=prod_id)

        # Mask
        self.mask += [(prod_id, single_processed_configs[0])]
        LOGGER.debug("Mask config append.", prod_id=prod_id)

        # Data
        self.data += [(prod_id, single_processed_configs[1])]
        LOGGER.debug("Data config append.", prod_id=prod_id)

        # Prod
        self.prod += [(prod_id, single_processed_configs[2])]
        LOGGER.debug("Prod config append.", prod_id=prod_id)

        self.nb_components += single_processed_configs[3]
        self.error_components += single_processed_configs[4]
        LOGGER.debug(
            "All configs for a prod append.",
            prod_id=prod_id,
            elapsed_time=time() - t0,
        )
        self.traited += 1
        LOGGER.info(f"Configuration treated {prod_id} {self.traited} ")

    def resouce_conf(self, prod_id, data):
        t1 = time()
        LOGGER.debug("Starting data config integration", prod_id=prod_id)
        rhmanager = RHManager(settings=self.settings, rules=self.rules)

        for (file_id, param), rh_dico in data.items():
            t1_bis = time()
            key = " ".join([file_id, param])
            if key in self.data_config["preprocessed"]:
                continue

            # sources
            full_root_param, accum = self.rules.param_to_description(param)
            sources_dico = rhmanager.source_files_terms(
                data_config=self.data_config,
                file_id=file_id,
                param=full_root_param,
                accum=accum,
            )
            # for operational reason,
            # if we run in operationnal way (oper or dble), we force to OPER
            # otherwise we read in file
            # in file case, that must be coherent with value in extract configuration
            if self.experiment in ["OPER", "DBLE"]:
                for ressource in rh_dico:
                    ressource["experiment"] = self.experiment
                for source in self.data_config["sources"].values():
                    for step in source.values():
                        for alternate in step:
                            alternate["experiment"] = self.experiment

            self.data_config["preprocessed"][key] = {
                "resource_handler": rh_dico,
                "sources": sources_dico,
                "agg": {"param": full_root_param, "accum": accum},
            }
            LOGGER.debug(
                "Data config: preproc file added.",
                prod_id=prod_id,
                preproc_file=key,
                elapsed_time=time() - t1_bis,
            )
        LOGGER.debug(
            "All Data resouce added.",
            prod_id=prod_id,
            elapsed_time=time() - t1,
        )

    @property
    def version_config(self):
        return VersionConfig(
            version=self.hashcode,
            drafting_datetime=self.rules.drafting_datetime,
            reference_datetime=self.rules.reference_datetime,
            production_datetime=self.rules.bulletin_datetime,
            configuration_datetime=self.get_configuration_datetime(),
        )

    def process_all(self, nproc: int = cpu_count()):
        """process_all

        Returns:
            (dict, dict, dict): Tuple of all three expected configuration
                dictionnaries (mask, data and production)
        """
        # sorted by nunmber of components

        LOGGER.info("Trying to load the configuration file...", func="__init__")
        configs = config_metronome(self.settings.config_filename)
        LOGGER.info("configuration file loaded.", func="__init__")
        self.set_confhash(configs)
        self.set_configuration_datetime(configs)
        self.data_config = {
            "config_version": self.hashcode,
            "sources": dict(),
            "preprocessed": dict(),
        }
        # use list instead of direct dict
        # due to dictionary changed size during iteration RuntimeError
        self.data = []
        self.prod = []
        self.mask = []
        self.traited = 0
        self.nb_components = 0
        self.error_components = 0
        config_global = ConfigGlobal(
            self.experiment,
            self.hashcode,
            self.settings,
            self.rules,
            self.get_geo,
            self.list_components_configs,
        )
        parallel = Parallel(processes=nproc)
        for config in configs:
            prod_id = config.setdefault("production_id", getpid())
            parallel.apply(
                self.process_single_prod,
                args=(config_global, config),
                callback=self.append_config,
                task_name=prod_id,
            )

        parallel.run(timeout=self.settings.timeout)
        self.mask_config = {mask[0]: mask[1] for mask in self.mask}
        self.prod_config = {prod[0]: prod[1] for prod in self.prod}
        t1 = time()
        [self.resouce_conf(resource[0], resource[1]) for resource in self.data]
        if self.error_components > 0:
            LOGGER.error(
                f"Components : {self.nb_components} valids "
                f"and {self.error_components} errors"
            )
        else:
            LOGGER.info(
                f"Components : {self.nb_components} valids "
                f"and {self.error_components} errors"
            )
        # for i in range(len(self.config)):
        # prod_id = self.config[i].get("production_id", i)
        # self.resouce_conf(self.data[prod_id], prod_id)
        LOGGER.info(
            "Data resouces added.",
            elapsed_time=time() - t1,
        )

    def dump_configs(self, settings=None):
        # Dumping configs
        if settings:
            mask_config_filename = settings.mask_config_filename
            data_config_filename = settings.data_config_filename
            prod_config_filename = settings.prod_config_filename
            version_config_filename = settings.version_config_filename
        else:
            mask_config_filename = "mask.json"
            data_config_filename = "data.json"
            prod_config_filename = "prod.json"
            version_config_filename = "vers.json"
        JsonFile(mask_config_filename).dump(self.mask_config)
        JsonFile(data_config_filename).dump(self.data_config)
        JsonFile(prod_config_filename).dump(self.prod_config)
        JsonFile(version_config_filename).dump(self.version_config)

"""
@package configuration.components

component for Config processor module
"""

from copy import deepcopy
from time import time

# Standard packages
from typing import List

from mfire import composite

# local package
from mfire.configuration.levels import LevelManager
from mfire.configuration.weathers import WeatherManager

# Own package
from mfire.settings import TEXT_ALGO, get_logger
from mfire.utils.exception import ConfigurationError, ConfigurationWarning

# Third parties packages


# Logging
LOGGER = get_logger(name="config_processor.mod", bind="config_processor")
DEFAULT_TIME_DIMENSION = "valid_time"  # TODO: put it in the csv settings files
ComponentComposites = (
    composite.RiskComponentComposite | composite.TextComponentComposite
)


class GenericComponent:
    def __init__(self, componentmanager, compobase, bounding, compo_config):
        self.componentmanager = componentmanager
        self.compobase = compobase
        self.box = bounding.get_box_geos(compo_config)
        self.compo_config = compo_config

    def change_hazard_name(
        self,
        processed_compo_config,
    ):
        LOGGER.debug(f"Abstract method with {processed_compo_config}")

    def append_compo(
        self,
        new_compo_config,
        processed_compo_config,
        bulletin_datetime,
        files_groups,
        params,
    ):
        LOGGER.debug(
            f"Abstract method with {new_compo_config} {processed_compo_config}"
            f"{bulletin_datetime}{files_groups}{params}"
        )
        return []

    def process_single_component(
        self,
    ) -> List[ComponentComposites]:
        """process_single_component :"""
        result = []
        global LOGGER
        compo_hazard = self.compo_config.get(
            "hazard_name", self.compo_config.get("hazard_id", "text")
        )
        compo_id = self.compo_config.get("id")
        LOGGER = LOGGER.bind(
            compo_id=compo_id,
            period_id=self.compo_config.get("period"),
            compo_hazard=compo_hazard,
        )
        try:
            LOGGER.info(
                "Starting to process component...",
                func="process_single_component",
            )
            t1 = time()

            processed_compo_config = deepcopy(self.compo_config)

            # Component's params
            params = self.get_components_params()

            # Component's period
            processed_period = self.compobase.processed_periods.get(
                self.compo_config.get("period")
            )
            processed_compo_config["period"] = processed_period
            self.change_hazard_name(processed_compo_config)

            # Component's geos
            files_groups = dict()
            for geo_id in self.compo_config["geos"]:
                LOGGER = LOGGER.bind(geo_id=geo_id)
                LOGGER.info(f"geo_id {geo_id}")
                geometries = self.componentmanager.useable_geometries(
                    self.compobase.all_shapes.get(geo_id, None)
                )
                try:
                    self.componentmanager.rhmanager.rules.best_preprocessed_files(
                        start=processed_period.start,
                        stop=processed_period.stop,
                        geometries=geometries,
                        params=params,
                    )
                    best_files = tuple(
                        self.componentmanager.rhmanager.rules.best_preprocessed_files(
                            start=processed_period.start,
                            stop=processed_period.stop,
                            geometries=geometries,
                            params=params,
                        )
                    )
                    if len(best_files) == 0:
                        LOGGER.warning(
                            f"No preprocessed file found for"
                            f" start={processed_period.start}"
                            f"stop={processed_period.stop}; geometries={geometries}; "
                            f"params={params}",
                        )
                    else:
                        if best_files in files_groups:
                            files_groups[best_files] += [geo_id]
                        else:
                            files_groups[best_files] = [geo_id]
                except ConfigurationWarning as c:
                    LOGGER.warning(c)
                except ConfigurationError as c:
                    LOGGER.error(c)
            LOGGER = LOGGER.try_unbind("mask_id")
            if len(files_groups) == 0:
                raise ConfigurationError("None Files group found")
            LOGGER.info(
                "Files group created",
                func="process_single_component",
                params=list(params),
                files_groups=[
                    [list(best_files), list(geos)]
                    for best_files, geos in files_groups.items()
                ],
            )

            result = self.generate_components_list(
                processed_compo_config=processed_compo_config,
                files_groups=files_groups,
                params=params,
            )
            LOGGER.info(
                "Component processed.",
                elapsed_time=time() - t1,
                func="process_single_prod",
            )
        except BaseException as b:
            LOGGER.error(
                f"Failed to process component : {b}",
                exc_info=True,
            )
        LOGGER = LOGGER.try_unbind("compo_id", "compo_hazard")
        return result

    def get_components_params(self):
        """get_components_params : Method which returns all the parameters
        used in the component or linked to the component.

        Args:
            compo_config (dict): Component config

        Returns:
            set : Set of parameter used in the component or linked.
        """
        return set()

    def generate_components_list(
        self,
        processed_compo_config: dict,
        files_groups: dict,
        params,
    ) -> list:
        """generates a list of ComponentComposite from a configuration

        Args:
            processed_compo_config (dict): base configuration of the componentss
            single_mask_config (MaskConfig): Mask used by the components
            compo_config (dict): configuration of the components
            files_groups (dict): Data files needed by the components
            params (set): Meteorolical parameters
            single_data_config (dict): resource_handlers

        Returns:
            list: the component composites generated from the refactored configuration
        """

        new_compo_config = deepcopy(processed_compo_config)

        new_compo_config["time_dimension"] = DEFAULT_TIME_DIMENSION
        new_compo_config[
            "production_datetime"
        ] = self.componentmanager.rhmanager.rules.bulletin_datetime
        new_compo_config[
            "configuration_datetime"
        ] = self.componentmanager.configuration_datetime

        new_components_list = self.append_compo(
            new_compo_config,
            processed_compo_config,
            self.componentmanager.rhmanager.rules.bulletin_datetime,
            files_groups,
            params,
        )

        return new_components_list


class RiskComponent(GenericComponent):
    def get_components_params(self):
        """get_components_params : Method which returns all the parameters
        used in the component or linked to the component.

        Args:
            compo_config (dict): Component config

        Returns:
            set : Set of parameter used in the component or linked.
        """
        params = []
        rules = self.componentmanager.rhmanager.rules
        for level in self.compo_config["levels"]:
            for event in level["elementsEvent"]:
                full_root_param, accum = rules.param_to_description(event["field"])
                if full_root_param not in rules.param_link_df:
                    params += [event["field"]]
                    continue
                linked_root_params = [
                    p.split("__")
                    for p in rules.param_link_df[full_root_param].dropna().index
                ]
                params += [
                    rules.description_to_param(p, l, accum)
                    for p, l in linked_root_params
                ]

        return set(params)

    def change_hazard_name(
        self,
        processed_compo_config,
    ):
        if "name" not in processed_compo_config:
            LOGGER.info("Filling with hazard name", func="process_single_component")
            processed_compo_config["name"] = self.compobase.processed_hazards[
                self.compo_config["hazard"]
            ].get("name")

        if "otherNames" not in processed_compo_config:
            processed_compo_config["otherNames"] = self.compobase.processed_hazards[
                self.compo_config["hazard_id"]
            ].get("otherNames")

    def append_compo(
        self,
        new_compo_config,
        processed_compo_config,
        bulletin_datetime,
        files_groups,
        params,
    ):
        new_compo_config["levels"] = []
        new_components_list = []
        LOGGER.debug(f"unused variable bulletin_datetime {bulletin_datetime}")
        for best_files, geos in files_groups.items():

            for file_id, _, _ in best_files:
                for param in params:
                    if (file_id, param) not in self.compobase.single_data_config:
                        self.compobase.single_data_config[
                            (file_id, param)
                        ] = self.componentmanager.rhmanager.preprocessed_rh(
                            file_id, param
                        )

            geos_base = {
                "file": self.compobase.single_mask_config.file,
                "mask_id": geos,
            }

            new_compo_config["geos"] = geos

            new_compo_config["levels"] = []

            for file_id, start_time, stop_time in best_files:
                levelmanager = LevelManager(
                    compobase=self.compobase,
                    rhmanager=self.componentmanager.rhmanager,
                    geos_base=geos_base,
                    compo_config=processed_compo_config,
                    box=self.box,
                    file_id=file_id,
                    start_stop=(start_time, stop_time),
                )
                new_compo_config["levels"] += [
                    levelmanager.get_new_level(level=level)
                    for level in processed_compo_config["levels"]
                ]
            new_compo = composite.RiskComponentComposite(**new_compo_config)
            new_components_list.append(new_compo)
        return new_components_list


class TextComponent(GenericComponent):
    def get_components_params(self):
        """get_components_params : Method which returns all the parameters
        used in the component or linked to the component.

        Args:
            compo_config (dict): Component config

        Returns:
            set : Set of parameter used in the component or linked.
        """
        params = []
        for weather in self.compo_config["weather"]:
            algo_conf = TEXT_ALGO[weather["id"]][weather.get("algo", "generic")]
            params += set(d["field"] for d in algo_conf["params"].values())
            if weather["condition"] is not None:
                if "field" in weather["condition"]:
                    params += [weather["condition"]["field"]]
        return set(params)

    def append_compo(
        self,
        new_compo_config,
        processed_compo_config,
        bulletin_datetime,
        files_groups,
        params,
    ):
        weathermanager = WeatherManager(
            compobase=self.compobase,
            componentmanager=self.componentmanager,
            processed_compo_config=processed_compo_config,
            box=self.box,
            production_datetime=bulletin_datetime,
            files_groups=files_groups,
            params=params,
        )
        new_compo_config["weathers"] = [
            weathermanager.get_new_weather(weather=weather)
            for weather in processed_compo_config["weather"]
        ]

        new_compo = composite.TextComponentComposite(**new_compo_config)
        return [new_compo]


class ComponentFactory:
    @classmethod
    def getComponent(cls, componentmanager, compobase, bounding, compo_config):
        component_objects = {"risk": RiskComponent, "text": TextComponent}
        try:
            component_object = component_objects[compo_config.get("type", None)]
            component = component_object(
                componentmanager, compobase, bounding, compo_config
            )
            return component.process_single_component()
        except KeyError:
            raise ConfigurationError(
                f"Unexpected component type : {compo_config.get('type',None)}."
            )

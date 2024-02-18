"""
@package configuration.tools

functions for Config processor module
"""
from tarfile import is_tarfile
from tarfile import open as tar_open

import numpy as np

# Third parties package
import pandas as pd

# Own package
from mfire.settings import get_logger
from mfire.utils import MD5, JsonFile
from mfire.utils.exception import ConfigurationError

# local package

# Logging
LOGGER = get_logger(name="config_processor.mod", bind="config_functions")


def config_metronome(config_filename: str):
    """config_metronome: read a configuration file from metronome
    This file can be a single json, a json-contener tar or IOBase (?)
    Args:
        config_filename : path to file
    Returns:from mfire.configuration.datas import RHManager

        a configuration (dict or list of dict)
    """

    def add_config(config_json, nb_prod, config):
        if isinstance(config_json, list):
            config += config_json
            nb_prod += len(config_json)
        elif isinstance(config_json, dict):
            nb_prod += 1
            config += [config_json]
        else:
            raise ConfigurationError(
                f"Configuration is a {type(config)}," " while list or dict expected."
            )
        return nb_prod, config

    config = []
    nb_prod = 0
    try:
        if is_tarfile(config_filename):
            LOGGER.info("Configuration is in a tarfile", func="__init__")
            with tar_open(config_filename) as config_tar:
                members = config_tar.getmembers()
                for i, config_file in enumerate(members):
                    config_json = JsonFile(config_tar.extractfile(config_file)).load()
                    nb_prod, config = add_config(config_json, nb_prod, config)
                    LOGGER.info(f"File {i+1}/{len(members)} loaded", func="__init__")
            LOGGER.info(f"{nb_prod} productions loaded from a tgz", func="__init__")

        elif config_filename.name.endswith(".json"):
            config_json = JsonFile(config_filename).load()
            nb_prod, config = add_config(config_json, nb_prod, config)
            LOGGER.info("Configuration loaded from a JSON", func="__init__")
    except TypeError:
        # Cas où l'on passe un IOBase.
        config = JsonFile(config_filename).load()
        LOGGER.info("Configuration loaded from a content JSON", func="__init__")
    return config


def base_component_config(compo_config):
    """base_component_config: Returns the base configuration of a component
    given its original configuration

    Args:
        compo_config (dict): Component's original configuration

    Returns:
        dict: Component's base configuration
    """
    output = {}
    if "alt_min" in compo_config["data"]:
        output["alt_min"] = compo_config["data"].get("alt_min")
    if "alt_max" in compo_config["data"]:
        output["alt_max"] = compo_config["data"].get("alt_max")
    output.update(
        {
            "id": compo_config["id"],
            "type": compo_config["data"]["type"],
            "name": compo_config["name"],
            "customer": compo_config.get("customer", "unknown"),
            "customer_name": compo_config.get("customer_name", "unknown"),
            "production_id": compo_config.get("production_id", "UnknownProdId"),
            "production_name": compo_config.get("production_name", "UnknownProdName"),
            "product_comment": compo_config["data"].get("product_comment", True),
            "compass_split": compo_config["data"].get("compass_split", True),
            "altitude_split": compo_config["data"].get("altitude_split", True),
            "geos_descriptive": compo_config["data"].get("geos_descriptive", []),
        }
    )

    return output


def reshape_hazard(hazard_idx: int, hazard: dict, columns: list) -> pd.DataFrame:
    """reshape_hazard: transform dict to dataframe for hazard
    Args:
        hazard_idx: order of this hazard
        hazard: definition of this hazard
        columns: stored data from this hazard
    Returns:
        dtaframe: foramted hazard
    """
    global LOGGER
    hazard_df = pd.DataFrame(columns=columns)
    LOGGER = LOGGER.bind(hazard_id=hazard["id"])
    if isinstance(hazard["id"], (list, tuple)):
        LOGGER.warning("Given hazard_id as list (or tuple)", func="reshape_hazard")
        if len(hazard["id"]) > 1:
            raise ConfigurationError(
                "Given hazard_id as list or tuple, "
                f"of length {len(hazard['id'])} > 1",
                func="reshape_hazard",
            )
        hazard["id"] = hazard["id"][0]

    hazard_name = hazard.get("label", hazard.get("technical_name", "unknown"))
    if hazard_name == "unknwon":
        LOGGER.warning("Given hazard as no known name")
    for level_idx, level in enumerate(hazard["levels"]):
        for config_idx, config in enumerate(level["configs"]):
            for geo in config["geos"]:
                for period in config["periods"]:
                    new_line_df = pd.DataFrame(
                        {
                            "hazard_id": hazard["id"],
                            "period": period,
                            "hazard_name": hazard_name,
                            "geo": geo,
                            "hazard_idx": hazard_idx,
                            "level_idx": level_idx,
                            "config_idx": config_idx,
                        },
                        index=[0],
                    )
                    hazard_df = pd.concat(
                        [hazard_df, new_line_df],
                        ignore_index=True,
                    )
    LOGGER = LOGGER.try_unbind("hazard_id")
    return hazard_df


def reshape_risk_component(compo_config):
    """reshape_risk_component: Transform a risk component configuration
    into a Promethee's structure given a component configuration with
    a Metronome structure.
    TO DO : Explain changes between component's configurations structures

    Args:
        compo_config (dict): Component's configuration
            (with a Metronome's structure)

    Returns:
        list of dict : List of component's configuration following
            Promethee's structure
    """
    global LOGGER
    LOGGER = LOGGER.bind(compo_id=compo_config.get("id"))
    component_df = pd.DataFrame(
        columns=[
            "hazard_id",
            "period",
            "hazard_name",
            "geo",
            "hazard_idx",
            "level_idx",
            "config_idx",
        ]
    )
    for hazard_idx, hazard in enumerate(compo_config["data"]["hazards"]):
        try:
            haz_df = reshape_hazard(hazard_idx, hazard, component_df.columns)
            component_df = pd.concat([component_df, haz_df], ignore_index=True)
        except BaseException:
            LOGGER.error(
                "Failed to reshape hazard.",
                hazard_id=hazard.get("id"),
                exc_info=True,
            )
    component_df = component_df.set_index(
        ["hazard_id", "period", "hazard_name", "geo"]
    ).sort_index()

    grouped_components_dict = dict()
    for idx in set(component_df.index):
        key = idx[:3] + tuple(component_df.loc[idx].values.reshape(-1))
        if key in grouped_components_dict:
            grouped_components_dict[key] += [idx[3]]
        else:
            grouped_components_dict[key] = [idx[3]]

    reshaped_components = []
    local_component_config = base_component_config(compo_config)
    for key, value in grouped_components_dict.items():
        new_compo = {
            "hazard_id": key[0],
            "period": key[1],
            "geos": value,
            "hazard_name": key[2],
            "levels": [],
        }
        new_compo.update(local_component_config)
        levels_indices = component_df.loc[
            (key[0], key[1], key[2], value[0])
        ].values.reshape((-1, 3))
        for hidx, lidx, cidx in levels_indices:
            current_level = compo_config["data"]["hazards"][hidx]["levels"][lidx]
            current_config = current_level["configs"][cidx]
            current_level_config = {"level": current_level["level"]}
            current_level_config.update(current_config["dataModel"])
            new_compo["levels"] += [current_level_config]

        reshaped_components += [new_compo]
    LOGGER = LOGGER.try_unbind("compo_id", "hazard_id")
    return reshaped_components


def reshape_text_component(compo_config: dict):
    """reshape_text_component: Transform a text component configuration
    into a Promethee's structure given a component configuration with
    a Metronome structure.
    TO DO : Explain changes between component's configurations structures

    Args:
        compo_config (dict): Component's configuration
            (with a Metronome's structure)

    Returns:
        list of dict : List of component's configuration following
            Promethee's structure
    """
    component_df = pd.DataFrame(columns=["period", "geo", "weather_idx", "config_idx"])

    for weather_idx, weather in enumerate(compo_config["data"]["weather"]):
        for config_idx, config in enumerate(weather["configs"]):
            for period in config["periods"]:
                for geo in config["geos"]:
                    new_line_df = pd.DataFrame(
                        {
                            "period": period,
                            "geo": geo,
                            "weather_idx": weather_idx,
                            "config_idx": config_idx,
                        },
                        index=[0],
                    )
                    component_df = pd.concat(
                        [component_df, new_line_df],
                        ignore_index=True,
                    )

    component_df = component_df.set_index(["period", "geo"]).sort_index()

    grouped_components_dict = dict()
    for idx in set(component_df.index):
        key = (idx[0], *component_df.loc[idx].values.reshape(-1))
        grouped_components_dict.setdefault(key, []).append(idx[1])

    reshaped_components = []
    local_component_config = base_component_config(compo_config)

    for key, value in grouped_components_dict.items():
        new_compo = {"period": key[0], "geos": value, "weather": []}
        new_compo.update(local_component_config)

        weather_indices = component_df.loc[(key[0], value[0])]

        if isinstance(weather_indices, pd.Series):
            weather_indices = weather_indices.to_frame().T

        for widx, cidx in weather_indices.values:
            current_weather = compo_config["data"]["weather"][widx]
            current_config = current_weather["configs"][cidx]
            if current_config["dataModel"] is not None:
                new_compo["weather"] += [
                    {
                        "id": current_weather["id"],
                        "condition": current_config["dataModel"]["text"],
                    }
                ]
            else:
                new_compo["weather"] += [
                    {
                        "id": current_weather["id"],
                        "condition": None,
                    }
                ]

        reshaped_components += [new_compo]

    return reshaped_components


class BoundingBox:
    """
    obtain bounding box of a component area
    take care to compute only once this box due to its expensive cost
    so store bounds of each unique set of needed geos in boxs refere by
    its hashcode
    """

    def __init__(self, all_geos):
        """all geos as FeatureconfigCollection
        all_geos : geos in the production
        """
        self.all_geos = all_geos
        self.boxs = {}

    def hashcode(self, geos) -> str:
        """hashcode: uniqueness of set of geos"""
        geos_idsorted = sorted([geo.id for geo in geos])
        return MD5(geos_idsorted).hash

    def set_box(self, geos):
        """set_box: actual computation of bounds for those geos"""
        bounds = np.array([geo.shape.bounds for geo in geos])
        lonn, latn, _, _ = tuple(bounds.min(axis=0))
        _, _, lonx, latx = tuple(bounds.max(axis=0))
        return ((latx, latn), (lonn, lonx))

    def get_box_geos(self, component):
        """get_box_geos: from a component and all geos as FeatureconfigCollection,
        return the bounding box of needed geos (axes and geos_descriptives)
        To gain performance, computation is made only once
        for a given unique set of needed geos
        (criteria hashcode), the result is stored in the global dictionary boxs
        Args:
            component: a single component
        Returns:
            bounding box (tuple)
        """

        geos = []
        # get axes
        needed_axes = [
            geo
            for geo_id in component["geos"]
            for geo in self.all_geos
            if geo.id == geo_id
        ]
        geos.extend(needed_axes)
        # get geos_descriptive
        needed_gd = [
            geo
            for geo_id in component["geos_descriptive"]
            for geo in self.all_geos
            if geo.id == geo_id
        ]
        geos.extend(needed_gd)

        geo_hash = self.hashcode(geos)
        if geo_hash not in self.boxs.keys():
            # only compute if not already done
            self.boxs[geo_hash] = self.set_box(geos)
        return self.boxs[geo_hash]

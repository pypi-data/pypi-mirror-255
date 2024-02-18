"""
@package configuration.components

component for Config processor module
"""

from copy import deepcopy

# Standard packages
from typing import List

from mfire import composite
from mfire.configuration.component_base import CompoBase, ComponentManager

# local package
from mfire.configuration.config_composite import get_aggregation, get_new_threshold

# Own package
from mfire.settings import TEXT_ALGO
from mfire.utils.date import Datetime

# Third parties packages


# Logging


class WeatherManager:
    def __init__(
        self,
        compobase: CompoBase,
        componentmanager: ComponentManager,
        processed_compo_config: dict,
        box,
        production_datetime: Datetime,
        files_groups: List,
        params: List,
    ):
        self.compobase = compobase
        self.processed_compo_config = processed_compo_config
        self.rules = componentmanager.rhmanager.rules
        self.rhmanager = componentmanager.rhmanager
        self.box = box
        self.production_datetime = production_datetime
        self.params = params
        self.files_groups = files_groups

    def set_selection(self, start_stop, grid_name):
        # TODO :mesh_size = self.rules.geometries_df.loc[grid_name, "mesh_size"]
        mesh_size = 0.26
        return {
            "slice": {
                "valid_time": start_stop,
                "latitude": (
                    self.box[0][0] + mesh_size,
                    self.box[0][1] - mesh_size,
                ),
                "longitude": (
                    self.box[1][0] - mesh_size,
                    self.box[1][1] + mesh_size,
                ),
            }
        }

    def get_grid_name(self, file_id, param):
        return self.compobase.single_data_config[(file_id, param["field"])][0][
            "geometry"
        ]

    def get_name(self, file_id, param):
        return self.compobase.single_data_config[(file_id, param["field"])][0]["param"]

    def get_new_weather(
        self,
        weather: dict,
    ) -> dict:

        local_config = self.compobase.single_data_config
        slice_start = None
        slice_stop = None
        file_ids = []
        for best_files, geos in self.files_groups.items():

            for file_id, file_start, file_stop in best_files:

                file_start = Datetime(file_start)
                if slice_start is None or file_start < slice_start:
                    slice_start = file_start

                file_stop = Datetime(file_stop)
                if slice_stop is None or file_stop > slice_stop:
                    slice_stop = file_stop

                file_ids.append(file_id)

                for weather_id in self.params:
                    if (
                        file_id,
                        weather_id,
                    ) not in local_config:
                        local_config[
                            (file_id, weather_id)
                        ] = self.rhmanager.preprocessed_rh(file_id, weather_id)
            geos_base = {
                "file": self.compobase.single_mask_config.file,
                "mask_id": geos,
            }
        start_stop = (slice_start, slice_stop)
        new_weather = deepcopy(weather)

        algorithm = weather.get("algo", "generic")
        new_weather["algorithm"] = algorithm

        params = TEXT_ALGO[weather["id"]][algorithm]["params"].items()

        new_weather["params"] = {}

        for key, param in params:

            # if the parameter's data is spread into several files it's because
            # they do not have the same time step.
            # They wont have the same grid in ALPHA, so we'll have to interpolate them
            # in FieldComposite.compute()
            if isinstance(file_ids, list):
                file = [
                    local_config[(file_id, param["field"])][0]["local"]
                    for file_id in file_ids
                ]
                # we extrapolate the data to the finest grid, which will be the one used
                # for the closest dates, stored in the first file
                grid_name = self.get_grid_name(file_ids[0], param)
                # all the files have the same parameter
                name = self.get_name(file_ids[0], param)
            else:
                file = local_config[(file_ids, param["field"])][0]["local"]
                grid_name = self.get_grid_name(file_ids, param)
                name = self.get_name(file_ids, param)
            # field: FieldComposite
            # take some extra data off side borders to ensure to have all data
            # by extending the bounding box
            field_selection = self.set_selection(start_stop, grid_name)
            new_weather["params"][key] = composite.FieldComposite(
                file=file,
                selection=field_selection,
                grid_name=grid_name,
                name=name,
            )

        new_weather["production_datetime"] = self.production_datetime

        new_weather["period"] = self.processed_compo_config["period"]

        units = dict()
        for key, param in params:
            new_weather["geos"] = composite.GeoComposite(
                grid_name=grid_name,
                **geos_base,
            )
            # units
            units[key] = weather.get("algo", param["default_units"])

        new_weather["units"] = units

        new_weather["localisation"] = composite.LocalisationConfig(
            compass_split=self.processed_compo_config["compass_split"],
            altitude_split=self.processed_compo_config["altitude_split"],
            geos_descriptive=self.processed_compo_config["geos_descriptive"],
        )

        if weather["condition"] is not None:
            new_weather["condition"] = composite.EventComposite(
                field=composite.FieldComposite(
                    file=file,
                    selection=field_selection,
                    grid_name=grid_name,
                    name=name,
                ),
                plain=get_new_threshold(weather["condition"]["plain"]),
                category=weather["condition"]["category"],
                geos=composite.GeoComposite(
                    grid_name=grid_name,
                    **geos_base,
                ),
                aggregation=get_aggregation(
                    weather["condition"]["aggregation"], geos_base
                ),
                altitude=composite.AltitudeComposite.from_grid_name(
                    grid_name=grid_name,
                ),
            )

            # altitude: champ non implémenté dans la configuration métronome
            if "mountain" in weather["condition"]:
                new_weather["altitude"] = weather["condition"]["altitude"]
                for cond in new_weather["condition"]:
                    cond.mountain = get_new_threshold(weather["condition"]["mountain"])
                    cond.altitude = weather["condition"]["altitude"]

        return new_weather

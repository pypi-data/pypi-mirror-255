"""
@package configuration.components

component for Config processor module
"""

# Standard packages
from typing import Optional, Tuple

from pydantic import BaseModel

from mfire import composite
from mfire.configuration.component_base import CompoBase

# local package
from mfire.configuration.config_composite import get_aggregation, get_new_threshold
from mfire.configuration.datas import RHManager

# Own package
from mfire.settings import get_logger
from mfire.utils.date import Datetime

# Third parties packages


# Logging
LOGGER = get_logger(name="config_processor.mod", bind="config_processor")
DEFAULT_TIME_DIMENSION = "valid_time"  # TODO: put it in the csv settings files
DEFAULT_COMPUTE_LIST = ["density", "extrema", "representative", "summary"]

EventComposites = composite.EventComposite | composite.EventBertrandComposite
ComponentComposites = (
    composite.RiskComponentComposite | composite.TextComponentComposite
)


class BaseModelType(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class LevelManager(BaseModel):
    class Config:
        copy_on_model_validation = False

    compobase: Optional[CompoBase] = None
    rhmanager: Optional[RHManager] = None
    compo_config: Optional[dict] = None
    geos_base: Optional[dict] = None
    box: Tuple[Tuple[float, float], Tuple[float, float]]
    file_id: str
    start_stop: Tuple[Datetime, Datetime]

    def get_new_level(
        self,
        level: dict,
    ) -> composite.LevelComposite:
        global LOGGER
        LOGGER = LOGGER.bind(level=level["level"])

        new_level = {
            "level": level["level"],
            "probability": level.get("probability"),
            "logical_op_list": level["logicalOpList"],
            "aggregation_type": level["aggregationType"],
            "time_dimension": DEFAULT_TIME_DIMENSION,
            "compute_list": DEFAULT_COMPUTE_LIST,
        }

        # aggregation: Optional[Aggregation]
        aggregation_aval = None
        if "aggregation" in level:
            aggregation_aval = level["aggregation"]
            new_level["aggregation"] = get_aggregation(
                aggregation_aval, self.geos_base["file"], None
            )

        # localisation: LocalisationConfig
        new_level["localisation"] = composite.LocalisationConfig(
            compass_split=self.compo_config.get("compass_split", True),
            altitude_split=self.compo_config.get("altitude_split", True),
            geos_descriptive=self.compo_config.get("geos_descriptive", []),
        )

        # elements_event: List[Union[EventBertrandComposite, EventComposite]]
        eventmanager = EventManager(
            levelmanager=self,
            aggregation_aval=aggregation_aval,
        )
        new_level["elements_event"] = [
            eventmanager.get_new_event(event=event) for event in level["elementsEvent"]
        ]
        LOGGER.try_unbind("level")
        return composite.LevelComposite(**new_level)


class EventManager(BaseModel):
    class Config:
        copy_on_model_validation = False

    levelmanager: LevelManager
    aggregation_aval: Optional[dict] = None

    def get_new_event(
        self,
        event: dict,
    ) -> EventComposites:
        rhmanager = self.levelmanager.rhmanager
        rules = rhmanager.rules
        single_data_config = self.levelmanager.compobase.single_data_config
        geos_base = self.levelmanager.geos_base
        file_id = self.levelmanager.file_id
        start_stop = self.levelmanager.start_stop
        compo_config = self.levelmanager.compo_config
        box = self.levelmanager.box
        current_data_config = single_data_config[(file_id, event["field"])][0]
        grid_name = current_data_config["geometry"]
        global LOGGER
        LOGGER = LOGGER.bind(
            param=event["field"],
            grid_name=grid_name,
            func="get_new_event",
        )

        # list of stuff to pass on:
        composite_class = composite.EventComposite
        new_event = dict()
        # field: FieldComposite
        # take some extra data off side borders to ensure to have all data
        # by extending the bounding box
        # TODO : mesh_size = rules.geometries_df.loc[grid_name, "mesh_size"]
        mesh_size = 0.26
        field_selection = {
            "slice": {
                "valid_time": start_stop,
                "latitude": (
                    box[0][0] + mesh_size,
                    box[0][1] - mesh_size,
                ),
                "longitude": (
                    box[1][0] - mesh_size,
                    box[1][1] + mesh_size,
                ),
            }
        }
        new_event["field"] = composite.FieldComposite(
            file=current_data_config["local"],
            name=event["field"],
            grid_name=grid_name,
            selection=field_selection,
        )

        # category: Category
        new_event["category"] = event["category"]

        # TODO Since Metronome doesn't handle very well the only mountain case we have
        #  to handle it manually here
        if event.get("alt_min"):
            new_event["mountain"] = get_new_threshold(event["plain"])
        else:
            new_event["plain"] = get_new_threshold(event["plain"])
            if "mountain" in event:
                new_event["mountain"] = get_new_threshold(event["mountain"])

        # mountain_altitude: Optional[int]
        if "altitude" in event:
            new_event["mountain_altitude"] = event["altitude"][0]["mountainThreshold"]

        # altitude: Optional[AltitudeComposite]
        new_event["altitude"] = composite.AltitudeComposite.from_grid_name(
            grid_name=grid_name,
            alt_min=compo_config.get("alt_min"),
            alt_max=compo_config.get("alt_max"),
        )

        # geos: Optional[GeoComposite]
        new_event["geos"] = composite.GeoComposite(
            grid_name=grid_name,
            **geos_base,
        )

        # time_dimension: Optional[str]
        new_event["time_dimension"] = DEFAULT_TIME_DIMENSION

        # aggregation: Optional[Aggregation]
        if "aggregation" in event:
            new_event["aggregation"] = get_aggregation(
                event["aggregation"], geos_base["file"], grid_name
            )

        # aggregation_aval: Optional[Aggregation]
        new_event["aggregation_aval"] = get_aggregation(
            self.aggregation_aval, geos_base["file"], grid_name
        )

        # compute_list: Optional[list]
        new_event["compute_list"] = DEFAULT_COMPUTE_LIST

        # checking if in case of a BertrandEvent
        root_param = event["field"].split("__")[0]
        if root_param in rules.agg_param_df.index:
            # Cas special des arguments pour riskBertrand
            tmp_param, accum = rules.param_to_description(event["field"])
            model_step = int(rules.get_file_info(file_id)["step"])
            LOGGER.info(
                f"Parameter {event['field']} is inside agg_param_list. "
                "Checking for Bertrand risk.",
            )
            if accum > model_step:
                base_param, tmp_l = tmp_param.split("__")
                param_base = rules.description_to_param(base_param, tmp_l, model_step)
                LOGGER.info(
                    "Adding information for Bertrand risk. "
                    f"Param de base a cette echeance {param_base}",
                )
                if (file_id, param_base) not in single_data_config:
                    single_data_config[
                        (file_id, param_base)
                    ] = rhmanager.preprocessed_rh(file_id=file_id, param=param_base)
                new_event["field_1"] = composite.FieldComposite(
                    file=single_data_config[(file_id, param_base)][0]["local"],
                    name=param_base,
                    grid_name=grid_name,
                    selection=field_selection,
                )
                new_event["cum_period"] = accum
                composite_class = composite.EventBertrandComposite

        LOGGER.try_unbind("param", "grid_name", "func")
        return composite_class(**new_event)

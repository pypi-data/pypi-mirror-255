"""mfire.configuration module

This module handles version related to the configuration Handling

"""

from typing import Any

from pydantic import BaseModel, validator

from mfire.utils.date import Datetime


class ConfigGlobal:
    def __init__(
        self,
        experiment,
        config_hash,
        settings,
        rules,
        get_geo,
        list_components_configs,
    ):
        self.experiment = experiment
        self.config_hash = config_hash
        self.settings = settings
        self.rules = rules
        self.get_geo = get_geo
        self.list_components_configs = list_components_configs


class VersionConfig(BaseModel):
    """objet qui contient la version de la configuration

    Inheritance : BaseModel

    Returns:
        BaseModel : objet VersionConfig
    """

    version: str
    drafting_datetime: Datetime
    reference_datetime: Datetime
    production_datetime: Datetime
    configuration_datetime: Datetime

    @validator(
        "drafting_datetime",
        "reference_datetime",
        "production_datetime",
        "configuration_datetime",
        pre=True,
    )
    def check_datetimes(cls, v: Any) -> Datetime:
        return Datetime(v)

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Tuple, Union

import mfire.utils.mfxarray as xr
from mfire.localisation.localisation_manager import Localisation
from mfire.utils.date import Datetime


class ComponentInterface(ABC):
    """Interface for the Component Handler."""

    @property
    @abstractmethod
    def log_ids(self) -> Dict[str, str]:
        """Get information for logging purposes."""

    @abstractmethod
    def get_template_key(self) -> str:
        """Get the template key."""

    @abstractmethod
    def get_template_type(self, risk_level: int = None) -> str:
        """Get the template type."""

    @abstractmethod
    def get_production_datetime(self) -> Datetime:
        """Get the production date and time."""

    @abstractmethod
    def get_periods_name(self) -> list:
        """Get the names of periods."""

    @abstractmethod
    def get_areas_name(self) -> list:
        """Get the names of zones."""

    @abstractmethod
    def merge_area(self, da: Union[xr.DataArray, list]) -> xr.DataArray:
        """Merge areas in a data array."""

    @abstractmethod
    def get_critical_value(self) -> dict:
        """Get the critical values."""

    @abstractmethod
    def get_risk_name(self) -> str:
        """Get the risk name."""

    @classmethod
    @abstractmethod
    def open(cls, repo: str):
        """Open a ComponentHandler based on localization."""


class ComponentHandlerLocalisation(ComponentInterface):
    """Class for handling localization and comment generation modules."""

    def __init__(self, localisation_handler: Localisation):
        """Initialize a ComponentHandler based on a localization object.

        Args:
            localisation_handler (Localisation): The localization object.
        """
        self.localisation_handler = localisation_handler
        self.unique_table = self.localisation_handler.get_unique_table()
        self.alt_min, self.alt_max = self._get_alt_min_max()

    @property
    def log_ids(self) -> Dict[str, str]:
        """Get information for logging purposes."""
        return {
            "production_id": self.localisation_handler.component.production_id,
            "production_name": self.localisation_handler.component.production_name,
            "component_id": self.localisation_handler.component.id,
            "component_name": self.localisation_handler.component.name,
            "hazard_id": self.localisation_handler.component.hazard_id,
            "hazard_name": self.localisation_handler.component.hazard_name,
            "geo_id": self.localisation_handler.geo_id,
        }

    def get_template_key(self) -> str:
        """Get the template key."""
        return self.localisation_handler.get_unique_name()

    def get_template_type(self, risk_level: int = None) -> str:
        """Get the template type based on the given risk level.

        Args:
            risk_level (int, optional): The risk level. Defaults to None.

        Returns:
            str: The template type.
        """
        template_type = self.localisation_handler.get_level_type(risk_level)
        return template_type

    def get_production_datetime(self) -> Datetime:
        """Get the production date and time."""
        return self.localisation_handler.component.production_datetime

    def get_periods_name(self) -> list:
        """Get the names of periods."""
        return list(self.unique_table.period.values.tolist())

    def get_areas_name(self) -> list:
        """Get the names of zones."""
        return list(self.unique_table.areaName.values)

    def merge_area(self, da: Union[xr.DataArray, list]) -> xr.DataArray:
        """Merge areas in a data array.

        If a list is given, it selects from self.unique_table using a list of IDs.

        Args:
            da (Union[xr.DataArray, list]): The areas data array.

        Returns:
            xr.DataArray: The merged data array.
        """
        if isinstance(da, list):
            return self.merge_area(self.unique_table.sel(id=da))
        return self.localisation_handler.summarized_handler.merge_zones(
            da,
            alt_min=self.alt_min,
            alt_max=self.alt_max,
        )

    def get_unique_table(self) -> xr.DataArray:
        """Get the unique table."""
        return self.unique_table

    def get_critical_value(self) -> dict:
        """Get the critical values."""
        return self.localisation_handler.get_critical_values()

    def get_risk_name(self) -> str:
        """Get the risk name."""
        return self.localisation_handler.component.hazard_name

    @classmethod
    def open(cls, repo: str):
        """Open a ComponentHandler based on localization.

        Args:
            repo (str): The path for instantiating the localization object.

        Returns:
            cls: The initialized ComponentHandler.
        """
        return cls(Localisation.load(repo=repo))

    def _get_alt_min_max(self) -> Tuple[int, int]:
        """Get the min and max altitude used in the best level of
        self.localisation.component.

        These values are used to correct altitude-defined area names.

        Returns:
            Tuple[int, int]: The min and max altitudes to use.
        """
        max_level = self.localisation_handler.component.final_risk_max_level(
            self.localisation_handler.geo_id
        )
        levels = self.localisation_handler.component.levels
        if max_level > 0:
            levels = self.localisation_handler.component.risks_of_level(level=max_level)
        return min(lvl.alt_min for lvl in levels), max(lvl.alt_max for lvl in levels)

    def modify_template(self, areaIds: list):
        """Modify the template based on the given area IDs.

        Args:
            areaIds (list): The list of area IDs.
        """
        self.localisation_handler.summarized_handler.update_unique_table(areaIds)
        self.unique_table = self.localisation_handler.get_unique_table()

    def get_summarized_info(self) -> tuple:
        """Return a tuple with the unique table and the unique name.

        Returns:
            tuple: (unique_table, unique_name)
        """
        return self.localisation_handler.get_summarized_info()

    def get_areas_id(self) -> list:
        """Get the list of area IDs."""
        return list(self.unique_table.id.values.tolist())

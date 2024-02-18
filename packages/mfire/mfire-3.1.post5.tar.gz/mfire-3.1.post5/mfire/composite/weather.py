from typing import Dict, Optional

from pydantic import validator

import mfire.utils.mfxarray as xr
from mfire.composite.base import BaseComposite
from mfire.composite.events import EventComposite
from mfire.composite.fields import FieldComposite
from mfire.composite.geos import AltitudeComposite, GeoComposite
from mfire.composite.levels import LocalisationConfig
from mfire.settings import TEXT_ALGO, get_logger
from mfire.utils.date import Datetime
from mfire.utils.xr_utils import ArrayLoader, Loader, da_set_up

# Logging
LOGGER = get_logger(name="weather.mod", bind="weather")


class WeatherComposite(BaseComposite):
    """
    Represents a WeatherComposite object containing the configuration of weather
    conditions for the Promethee production task.

    Args:
        baseModel: Pydantic base model.

    Returns:
        baseModel: Weather object.
    """

    class Config:
        copy_on_model_validation = False

    id: str
    condition: Optional[EventComposite]
    params: Dict[str, FieldComposite]
    altitude: Optional[AltitudeComposite]
    geos: Optional[GeoComposite]
    localisation: LocalisationConfig
    production_datetime: Optional[Datetime] = Datetime()
    units: Dict[str, Optional[str]]
    algorithm: Optional[str] = "generic"
    _weathers_ds: xr.Dataset = xr.Dataset()
    _data: xr.Dataset = None

    @validator("params")
    def validate_params(cls, v, values):
        """
        Validates the keys of the params dictionary.

        Args:
            v: The params dictionary.
            values: The values of the model.

        Returns:
            Dict[str, FieldComposite]: The validated params dictionary.

        Raises:
            ValueError: If the keys of the params dictionary do not match the expected
                keys.
        """

        params_expected = TEXT_ALGO[values["id"]][values.get("algo", "generic")][
            "params"
        ].keys()

        if v.keys() != params_expected:
            raise ValueError(
                f"Wrong field: {list(v.keys())}, expected {list(params_expected)}"
            )
        return v

    @validator("production_datetime", pre=True)
    def init_datetime(cls, v: str) -> Datetime:
        """
        Initializes the production_datetime.

        Args:
            v: The production_datetime value.

        Returns:
            Datetime: The initialized production_datetime value.
        """
        return Datetime(v)

    @property
    def _cached_attrs(self) -> dict:
        """
        Returns the cached attributes dictionary.

        Returns:
            dict: The cached attributes dictionary.
        """
        return {"data": Loader}

    @property
    def check_condition(self) -> bool:
        """
        Checks if the condition is satisfied.

        Returns:
            bool: True if the condition is satisfied, False otherwise.
        """
        if self.condition is None:
            return False

        event_da = self.condition.compute()
        return bool(event_da.any().values)

    def _compute(self, **kwargs) -> xr.Dataset:
        """
        Computes the weather by following the specified steps.

        Returns:
            xr.Dataset: The computed weather dataset.
        """
        output_ds = xr.Dataset(
            {
                name: field.compute().reset_coords(drop=True)
                for name, field in self.params.items()
            }
        )

        # Add altitude field and take into account the altitude mask
        mask_da = 1.0
        if self.altitude is not None:
            output_ds["altitude"] = da_set_up(self.altitude.compute(), output_ds)
            mask_da = output_ds["altitude"].mask.f32

        # Take into account the geo mask
        if self.geos is not None:
            geo_mask_da = da_set_up(
                self.geos_data(kwargs.get("geo_id")), output_ds
            ).mask.f32
            mask_da = geo_mask_da * mask_da

        output_ds = output_ds * mask_da

        # Check if the variables are present
        for coord in ("areaName", "areaType"):
            if coord not in output_ds.coords:
                output_ds.coords[coord] = ("id", ["unknown"] * output_ds.id.size)

        return output_ds

    def geos_data(self, geo_id: Optional[str] = None) -> xr.DataArray:
        """
        Computes the geos data.

        Args:
            geo_id: Id of geo to take the geos data.

        Returns:
            xr.Dataset: The computed weather dataset.
        """
        geos = self.geos.compute()
        if geo_id is not None:
            geos = geos.sel(id=geo_id)
        return geos

    def geos_descriptive(self, geo_id: str) -> xr.DataArray:
        """
        Returns the descriptive geos DataArray.

        Args:
            geo_id: Id of geo to take the geos_descriptive.

        Returns:
            xr.DataArray: The descriptive geos DataArray.
        """
        geos = self.geos.mask_da
        allowed_area_types = []
        if self.localisation.altitude_split:
            allowed_area_types += ["Altitude"]
        if self.localisation.compass_split:
            allowed_area_types += ["compass"]
        ids = [
            id
            for id in geos.id.data
            if (
                (
                    id.startswith(f"{geo_id}_")
                    and geos.sel(id=id).areaType in allowed_area_types
                )
                or id in self.localisation.geos_descriptive
            )
        ]

        return geos.sel(id=ids)

    def altitudes(self, param: str) -> Optional[xr.DataArray]:
        """
        Returns the altitudes DataArray for a given parameter.

        Args:
            param: The parameter name.

        Returns:
            Optional[xr.DataArray]: The altitudes DataArray or None if not found.
        """
        try:
            return ArrayLoader.load_altitude(self.params[param].grid_name)
        except KeyError:
            return None

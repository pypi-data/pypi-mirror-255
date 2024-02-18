from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple, Union

from pydantic import validator

import mfire.utils.mfxarray as xr
from mfire.composite.base import BaseComposite
from mfire.settings import ALT_MAX, ALT_MIN, Settings, get_logger
from mfire.utils.xr_utils import ArrayLoader, MaskLoader

# Logging
LOGGER = get_logger(name="geos.mod", bind="geos")


class GeoComposite(BaseComposite):
    """
    Represents a GeoComposite object containing the configuration of the periods for
    the Promethee production task.

    Args:
        baseModel: BaseModel from the pydantic library.

    Returns:
        baseModel: GeoComposite object.
    """

    file: Path
    mask_id: Optional[Union[List[str], str]]
    grid_name: Optional[str]

    def _compute(self, **kwargs) -> xr.DataArray:
        """
        Computes the GeoComposite object by loading mask data from the file.

        Returns:
            xr.DataArray: Computed GeoComposite object.
        """
        return MaskLoader(filename=self.file, grid_name=self.grid_name).load(
            ids_list=kwargs.get("mask_id", self.mask_id)
        )

    @property
    def mask_da(self) -> xr.DataArray:
        return MaskLoader(filename=self.file, grid_name=self.grid_name).load()

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """
        Computes the bounds of the GeoComposite object.

        Returns:
            Tuple[float, float, float, float]: Bounds of the GeoComposite object as
                (min_lon, min_lat, max_lon, max_lat).
        """
        mask_da = self.compute()
        return (
            mask_da.longitude.values.min(),
            mask_da.latitude.values.min(),
            mask_da.longitude.values.max(),
            mask_da.latitude.values.max(),
        )


class AltitudeComposite(BaseComposite):
    """
    Represents an AltitudeComposite object containing the configuration of the fields
    for the Promethee production task.

    Args:
        baseModel: BaseModel from the pydantic library.

    Returns:
        baseModel: AltitudeComposite object.
    """

    filename: Path
    alt_min: Optional[int] = ALT_MIN
    alt_max: Optional[int] = ALT_MAX

    @validator("alt_min")
    def init_alt_min(cls, v: int) -> int:
        if v is None:
            return ALT_MIN
        return v

    @validator("alt_max")
    def init_alt_max(cls, v: int) -> int:
        if v is None:
            return ALT_MAX
        return v

    @validator("filename")
    def init_filename(cls, v: Path) -> Path:
        """
        Initializes the filename by converting it to a Path object and checking its
        existence.

        Args:
            v (Path): Input filename.

        Returns:
            Path: Initialized filename as a Path object.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        filename = Path(v)
        if not filename.is_file():
            raise FileNotFoundError(f"No such file {v}.")
        return filename

    def _compute(self, **_kwargs) -> xr.DataArray:
        """
        Computes and returns the computed field data based on the altitude file and
        altitude restrictions.

        Returns:
            xr.DataArray: Computed field data.
        """
        field_da = ArrayLoader(filename=self.filename).load()
        if self.alt_min is not None:
            field_da = field_da.where(field_da >= self.alt_min)
        if self.alt_max is not None:
            field_da = field_da.where(field_da <= self.alt_max)
        return field_da

    @classmethod
    def from_grid_name(
        cls,
        grid_name: str,
        alt_min: Optional[int] = None,
        alt_max: Optional[int] = None,
    ) -> AltitudeComposite:
        """
        Creates an AltitudeComposite object from the grid name and altitude
        restrictions.

        Args:
            grid_name (str): Grid name.
            alt_min (int, optional): Minimum altitude. Defaults to None.
            alt_max (int, optional): Maximum altitude. Defaults to None.

        Returns:
            AltitudeComposite: Created AltitudeComposite object.
        """
        return cls(
            filename=Path(Settings().altitudes_dirname) / f"{grid_name}.nc",
            alt_min=alt_min,
            alt_max=alt_max,
        )

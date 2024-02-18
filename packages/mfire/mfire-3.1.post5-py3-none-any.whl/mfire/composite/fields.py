"""
    Module d'interprétation de la configuration, objet fields
"""
from pathlib import Path
from typing import Any, List, Optional, Union

from pydantic import validator

import mfire.utils.mfxarray as xr
from mfire.composite.base import BaseComposite
from mfire.settings import get_logger
from mfire.utils.selection import Selection
from mfire.utils.unit_converter import unit_conversion
from mfire.utils.xr_utils import ArrayLoader, interpolate_to_new_grid

# Logging
LOGGER = get_logger(name="composite.fields.mod", bind="composite.fields")


class FieldComposite(BaseComposite):
    """
    Represents a FieldComposite object containing the configuration of the fields for
    the Promethee production task.

    Args:
        baseModel: Base model from the pydantic library.

    Returns:
        baseModel: FieldComposite object.
    """

    file: Union[Path, List[Path]]
    selection: Optional[Selection] = None
    grid_name: str
    name: str

    @validator("selection", always=True)
    def check_selection(cls, v):
        """
        Checks and initializes the selection criteria.

        Args:
            v: Input selection criteria.

        Returns:
            Selection: Initialized selection criteria.
        """
        if v is None:
            return Selection()
        return v

    def _compute(self, **_kwargs) -> xr.DataArray:
        """
        Computes and returns the computed field data based on the file and selection
        criteria.
        """

        field_da = None

        # we can either have a single file (if all the data for the Period have the same
        # time step)
        # or a list of files (if the data have heterogeneous time steps).
        if isinstance(self.file, list):
            for file in self.file:
                new_field_da = ArrayLoader(filename=file).load(selection=self.selection)
                # we filter out the useless data (out of bound points and dates)
                # for each file instead of doing it after the concat to heavily reduce
                # memory use (on "big" axes, like EIC20, we divide it by 3)

                if field_da is None:
                    field_da = new_field_da
                else:
                    # first, we make sure all tha data are on the same grid
                    # then we remove the dates that are on both DataArrays
                    # (we keep the first because it's the one which
                    # has not been interpolated : the further in the future we are, the
                    # coarser the grid is)
                    new_field_da = unit_conversion(new_field_da, field_da.units)
                    new_field_da = interpolate_to_new_grid(new_field_da, self.grid_name)
                    field_da = xr.DataArray(
                        xr.concat([field_da, new_field_da], dim="valid_time")
                    ).drop_duplicates(dim="valid_time", keep="first")
        else:
            field_da = ArrayLoader(filename=self.file).load(selection=self.selection)

        LOGGER.debug(
            "Opening Field file",
            filename=self.file,
            da_name=field_da.name,
            da_grid_name=field_da.attrs.get("PROMETHEE_z_ref"),
            shape=field_da.shape,
            dims=field_da.dims,
        )
        return field_da

    def get_coord(self, coord_name: str) -> Any:
        """
        Retrieves the coordinate values based on the coordinate name.

        Args:
            coord_name (str): Name of the coordinate.

        Returns:
            Any: Coordinate values.
        """
        with xr.open_dataarray(self.file) as tmp_da:
            return tmp_da[coord_name].load()

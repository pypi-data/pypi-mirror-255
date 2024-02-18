"""
    Module d'interprétation de la configuration, objet fields
"""
from itertools import combinations
from typing import Iterable, Optional

from pydantic import BaseModel, root_validator, validator

import mfire.utils.mfxarray as xr
from mfire.settings import get_logger
from mfire.utils.date import Datetime

# Logging
LOGGER = get_logger(name="composite.fields.mod", bind="composite.fields")


class Selection(BaseModel):
    """
    Represents a Selection object.

    Args:
        baseModel: Base model from the pydantic library.

    Returns:
        baseModel: Selection object.
    """

    sel: Optional[dict] = {}
    slice: Optional[dict] = {}
    isel: Optional[dict] = {}
    islice: Optional[dict] = {}

    @root_validator(pre=False)
    def check_all_keys(cls, values: dict):
        """
        Validates that all keys are present in the Selection object.

        Args:
            values (dict): Input dictionary of values.

        Returns:
            dict: Updated dictionary of values.
        """
        set_sel = set(values.get("sel", {}))
        set_slice = set(values.get("slice", {}))
        set_isel = set(values.get("isel", {}))
        set_islice = set(values.get("islice", {}))

        if any(
            set_1.intersection(set_2)
            for set_1, set_2 in combinations(
                [set_sel, set_slice, set_isel, set_islice], r=2
            )
        ):
            raise ValueError("Same keys are found!")

        return values

    @validator("sel", "slice", pre=True)
    def check_valid_times(cls, value: dict):
        """
        Checks and converts valid_time values to np.datetime64 format.

        Args:
            value (dict): Input dictionary of values.

        Returns:
            dict: Updated dictionary of values.
        """
        if isinstance(value.get("valid_time"), Iterable):
            value["valid_time"] = [
                Datetime(dt).as_np_dt64 for dt in value["valid_time"]
            ]
        return value

    @validator("slice", "islice")
    def init_slices(cls, value: dict) -> dict:
        """
        Initializes slice values based on the input dictionary.

        Args:
            value (dict): Input dictionary of values.

        Returns:
            dict: Updated dictionary of values.
        """
        return {
            k: slice(*v) if isinstance(v, Iterable) else v for k, v in value.items()
        }

    def select(self, da: xr.DataArray) -> xr.DataArray:
        """
        Selects the data based on the defined indices and slices.

        Args:
            da (xr.DataArray): Input DataArray.

        Returns:
            xr.DataArray: Selected data.
        """
        return da.isel(**self.isel, **self.islice).sel(**self.sel, **self.slice)

    @property
    def all(self) -> dict:
        """
        Returns a dictionary containing all the selection criteria.

        Returns:
            dict: All selection criteria.
        """
        return {**self.sel, **self.slice, **self.isel, **self.islice}

    def update(
        self,
        new_sel: dict,
        new_slice: dict,
        new_isel: dict,
        new_islice: dict,
    ):
        """
        Updates the current selection criteria with new ones.

        Args:
            new_sel (dict): Dictionary of selection criteria.
            new_slice (dict): Dictionary of slice criteria.
            new_isel (dict): Dictionary of isel criteria. Defaults to None.
            new_islice (dict): Dictionary of islice criteria. Defaults to {}.
        """
        # creating new selection
        new_sel = Selection(
            new_sel=new_sel,
            new_slice=new_slice,
            new_isel=new_isel,
            new_islice=new_islice,
        )

        self.sel.update(new_sel.sel)
        self.slice.update(new_sel.slice)
        self.isel.update(new_sel.isel)
        self.islice.update(new_sel.islice)

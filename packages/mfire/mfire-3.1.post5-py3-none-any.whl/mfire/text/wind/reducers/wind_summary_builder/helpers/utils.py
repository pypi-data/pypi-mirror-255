from __future__ import annotations

from typing import Any, Optional

import mfire.utils.mfxarray as xr


def coords_dict_from_xr_coords(
    coords: xr.Coordinates,
    replace: dict,
    exclude: Optional[list[str]] = None,
) -> dict:
    """Replace somme coordinates of a given instance of xr.Coordinate."""
    coords_new: dict = {}
    for coord in coords.keys():
        if coord in replace:
            coords_new[coord] = replace[coord]
        elif exclude is not None and coord in exclude:
            continue
        else:
            coords_new[coord] = coords[coord].values

    return coords_new


def get_dict_value_from_keys_path(input_dict: dict, keys_path: list) -> Any:
    """Get a dictionary value from a key path."""
    value: Any = input_dict

    for key in keys_path:
        value: dict = value.get(key)
        if value is None:
            break

    return value

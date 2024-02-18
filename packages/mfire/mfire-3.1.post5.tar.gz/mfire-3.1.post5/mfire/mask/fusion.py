from itertools import combinations
from typing import Dict, List

import mfire.utils.mfxarray as xr
from mfire.localisation import compute_IoU
from mfire.settings import get_logger
from mfire.utils.xr_utils import finest_grid_name

# Logging
LOGGER = get_logger(name="mask_processor", bind="fusion")


def extract_area_name(properties: dict) -> str:
    """This enables to extract the name of the area from the configurations

    Args:
        properties ([dict]): The properties dictionary.
        This dictionary may contain "label", "alt_label", "name"

    Raises:
        ValueError: If we are not able to name the area we raise an error

    Returns:
        [str]: The areaName
    """
    for key in ("name", "label", "alt_label", "areaName", "area_name"):
        if key in properties and properties.get(key):
            return properties[key]
    raise ValueError(
        "Name was not found. Label cannot be split using '_' in 1 "
        "or 4 elements. alt_label was empty."
    )


class FusionZone:
    """
    Keeps information needed to create a fusion later.

    Args:
        area_da (xr.DataArray): The entire zones DataArray.
        axe_id (str): The axis that integrates the fused zones, in order to generate
            the ID.
        dims (Dimension): The variable used as dimensions (lat, lon generally).
    """

    def __init__(self, mask_ds: xr.Dataset, axe_id: str):
        self.mask_ds = mask_ds
        self.axe_id = axe_id

        grid_ref = finest_grid_name(self.mask_ds)
        self.area_da = self.mask_ds[grid_ref].mask.bool
        self.dims = ("latitude_" + grid_ref, "longitude_" + grid_ref)

        self.ids_list = []

        axe = self.area_da.sel(id=self.axe_id)
        for zone_id in self.area_da["id"].values:
            zone = self.area_da.sel(id=zone_id)
            inter_zone_axe = (axe * zone).sum(self.dims)
            if (
                zone.sum(self.dims) > 0
                and inter_zone_axe / zone.sum(self.dims) > 0.9
                and inter_zone_axe / axe.sum(self.dims) < 0.97
            ):
                self.ids_list.append(zone_id)

    def check_union_differs(self, id1: str, id2: str) -> bool:
        """
        Checks if the union of zones `id1` and `id2` is different from any other zone.

        Args:
            id1 (str): The ID of the first zone.
            id2 (str): The ID of the second zone.

        Returns:
            bool: True if the union is different, False otherwise.
        """
        z1 = self.area_da.sel(id=id1)
        z2 = self.area_da.sel(id=id2)
        my_zone = z1 + z2

        iou = compute_IoU(my_zone, self.area_da.sel(id=self.ids_list), dims=self.dims)
        return iou.max().data <= 0.9

    def check_zones_differ(self, id1: str, id2: str):
        """
        Checks if zones (referred to as id1 and id2) differ.

        Args:
            id1 (str): The ID of the first zone.
            id2 (str): The ID of the second zone.

        Returns:
            bool: True if the zones differ, False otherwise.
        """
        z1 = self.area_da.sel(id=id1)
        z2 = self.area_da.sel(id=id2)
        inter_zones = (z1 * z2).sum(self.dims)
        return (
            inter_zones / z1.sum(self.dims) < 0.1
            and inter_zones / z2.sum(self.dims) < 0.1
        )

    def compute(self) -> List[Dict]:
        """
        Create a dictionary to prepare the fusion.

        Args:
            id1, id2 (str): References to two zones to fuse.

        Returns:
            dict: A dictionary that stores the information needed to fuse.
        """
        result = []
        for id1, id2 in combinations(self.ids_list, r=2):
            if self.check_union_differs(id1, id2) and self.check_zones_differ(id1, id2):
                area_name1 = self.mask_ds["areaName"].sel(id=id1).data
                area_name2 = self.mask_ds["areaName"].sel(id=id2).data
                if area_name2 < area_name1:
                    area_name1, area_name2 = area_name2, area_name1
                result.append(
                    {
                        "name": f"{area_name1} et {area_name2}",
                        "base": [id1, id2],
                        "id": "__".join([self.axe_id, id1, id2]),
                        "areaType": "fusion2",
                    }
                )
        return result

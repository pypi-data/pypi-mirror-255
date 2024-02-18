import copy
from typing import Dict, List, Optional, Sequence, Tuple, Union

import mfire.utils.mfxarray as xr
from mfire.localisation import AltitudeInterval, rename_alt_min_max
from mfire.settings import ALT_MAX, ALT_MIN, LANGUAGE, SPACE_DIM, Dimension, get_logger

__all__ = ["compute_IoU", "RiskArea"]

# Logging
LOGGER = get_logger(name="areaAlgebra", bind="areaAlgebra")

DEFAULT_IOU = 0.5
DEFAULT_IOU_ALT = 0.7  # Pour nommer une zone "spatiale" par une zone d'altitude


def compute_IoU(
    left_da: xr.DataArray,
    right_da: xr.DataArray,
    dims: Dimension = SPACE_DIM,
) -> xr.DataArray:
    """Compute the IoU of two given binary dataarrays along the given dimensions.

    We may interpret the IoU (Intersection over Union) as a similarity score
    between two sets. Considering two sets A and B, an IoU of 1 means they are
    identical, while an IoU of 0 means they are completly disjoint.
    Using dims = ("latitude", "longitude") means that we want to find the most
    similarity between spatial zones.

    For example, this is the most common use case:
    >>> lat = np.arange(10, 0, -1)
    >>> lon = np.arange(-5, 5, 1)
    >>> id0 = ['a', 'b']
    >>> id1 = ['c', 'd', 'e']
    >>> arr0 = np.array(
    ... [[[int(i > k) for i in lon] for j in lat] for k in range(len(id0))]
    ... )
    >>> arr1 = np.array(
    ... [[[int(j > 5 + k) for i in lon] for j in lat] for k in range(len(id1))]
    ... )
    >>> da0 = xr.DataArray(arr0, coords=(("id0", id0), ("lat", lat), ("lon", lon)))
    >>> da1 = xr.DataArray(arr1, coords=(("id1", id1), ("lat", lat), ("lon", lon)))
    >>> da0
    <xarray.DataArray (id0: 2, lat: 10, lon: 12)>
    array([[[...]]])
    Coordinates:
    * id0      (id0) <U1 'a' 'b'
    * lat      (lat) int64 10 9 8 7 6 5 4 3 2 1
    * lon      (lon) int64 -6 -5 -4 -3 -2 -1 0 1 2 3 4 5
    >>> da1
    <xarray.DataArray (id1: 3, lat: 10, lon: 12)>
    array([[[...]]])
    Coordinates:
    * id1      (id1) <U1 'c' 'd' 'e'
    * lat      (lat) int64 10 9 8 7 6 5 4 3 2 1
    * lon      (lon) int64 -6 -5 -4 -3 -2 -1 0 1 2 3 4 5
    >>> compute_IoU(da0, da1, dims=("lat", "lon"))
    <xarray.DataArray (id0: 2, id1: 3)>
    array([[0.29411765, 0.25641026, 0.21126761],
        [0.25      , 0.22222222, 0.1875    ]])
    Coordinates:
    * id0      (id0) <U1 'a' 'b'
    * id1      (id1) <U1 'c' 'd' 'e'

    In this example, we created 2 binary dataarrays da0 and da1 containing
    respectively the zones ('a', 'b') and ('c', 'd', 'e'). The IoU returns us a table
    of the IoUs of all the combinations of the 2 sets of zones.

    make sure entries are of type booleans to be more efficient

    Args:
        left_da (xr.DataArray): Left dataarray
        right_da (xr.DataArray): Right DataArray
        dims (Dimension): Dimensions to apply IoU on.
            Defaults to SPACE_DIM.

    Returns:
        xr.DataArray: Table of the computed IoU along the given dims.
    """
    if left_da.dtype != "bool":
        left_da = left_da.astype("int8").astype("bool")
    if right_da.dtype != "bool":
        right_da = right_da.astype("int8").astype("bool")

    return (left_da * right_da).sum(dims) / (right_da + left_da).sum(dims)


def compute_IoL(
    geos_descriptive: xr.DataArray,
    phenomenon_map: xr.DataArray,
    dims: Dimension = SPACE_DIM,
    threshold_area_proportion: float = 0.25,
    threshold_phenomenon_proportion: float = 0.1,
) -> Optional[xr.DataArray]:
    """
    Compute the IoL of two given binary dataarrays along the given dimensions.
    We may interpret the IoL (Intersection over Location) as a similarity score
    between two sets. Make sure entries are of type booleans to be more efficient

    Args:
        geos_descriptive (xr.DataArray): Containing all geos descriptive with different
                                        ids
        phenomenon_map (xr.DataArray): Map of the phenomenon
        dims (Dimension): Dimensions to apply IoL on.
            Defaults to SPACE_DIM.
        threshold_area_proportion (float): Minimal proportion of the phenomenon in an
            area over the size of area
        threshold_phenomenon_proportion (float): Minimal proportion of the phenomenon in
            an area over the size of phenomenon

    Returns:
        xr.DataArray: Table of the computed IoL along the given dims.
    """

    if geos_descriptive.dtype != "bool":
        geos_descriptive = geos_descriptive.astype("int8").astype("bool")
    if phenomenon_map.dtype != "bool":
        phenomenon_map = phenomenon_map.astype("int8").astype("bool")
    if "id" in phenomenon_map.dims:
        phenomenon_map = phenomenon_map.sum("id")

    phenomenon_size = phenomenon_map.sum()

    # we drop the zones which have a proportion of the phenomenon below the threshold
    inter = (geos_descriptive * phenomenon_map).sum(dims)
    geos_prop = inter / geos_descriptive.sum(dims)
    phenomenon_prop = inter / phenomenon_map.sum(dims)
    remaining_area = geos_descriptive[
        (geos_prop >= threshold_area_proportion)
        & (phenomenon_prop >= threshold_phenomenon_proportion)
    ]

    ids = []
    selected_prop = 0.0
    while remaining_area.count() > 0 and selected_prop < 0.9:
        map_with_exclusions = remaining_area
        if ids:
            map_with_exclusions *= geos_descriptive.sel(id=ids).sum("id") == 0
        phenomenon_map_with_exclusions = map_with_exclusions * phenomenon_map

        phenomenon_proportion = phenomenon_map_with_exclusions.sum(
            dims
        ) / map_with_exclusions.sum(dims)
        cond = phenomenon_proportion > phenomenon_proportion.max() - 0.1

        id_to_take = phenomenon_map_with_exclusions[cond].sum(dims).idxmax().item()
        ids.append(id_to_take)

        sorted_areas = geos_descriptive.sel(id=ids).sum("id") > 0
        selected_prop = (phenomenon_map * sorted_areas).sum() / phenomenon_size

        remaining_area = remaining_area.drop_sel(id=id_to_take)
        if remaining_area.count() > 0:
            inter = (remaining_area * phenomenon_map * ~sorted_areas).sum(dims)
            geos_prop = inter / remaining_area.sum(dims)
            phenomenon_prop = inter / phenomenon_map.sum(dims)

            remaining_area = remaining_area[
                (geos_prop >= threshold_area_proportion)
                & (phenomenon_prop >= threshold_phenomenon_proportion)
            ]

    if not ids:
        return None

    # we delete subareas contained in a selected area
    sorted_areas = geos_descriptive.sel(id=ids)
    sorted_areas = sorted_areas.sortby(sorted_areas.sum(dims), ascending=False)
    sorted_ids = sorted_areas.id
    i = 0
    while i < len(sorted_ids):
        ids_to_exclude = []
        for j in range(i + 1, len(sorted_ids)):
            map_with_exclusions = sorted_areas.isel(id=j) > 0
            map_size = map_with_exclusions.sum(dims)
            for k in range(i + 1):
                map_with_exclusions &= ~sorted_areas.isel(id=k) > 0

            # We exclude the nested location
            geo_prop = (map_with_exclusions & phenomenon_map).sum(dims) / map_size
            if geo_prop < threshold_area_proportion:
                ids_to_exclude.append(j)
        if ids_to_exclude:
            sorted_ids = sorted_ids.drop_isel(id=ids_to_exclude)
        i += 1

    return geos_descriptive.sel(id=[id for id in ids if id in sorted_ids])


def compute_IoLeft(
    left_da: xr.DataArray,
    right_da: xr.DataArray,
    dims: Dimension = SPACE_DIM,
) -> xr.DataArray:
    """Compute the IoL of two given binary dataarrays along the given dimensions.

    Args:
        left_da (xr.DataArray): Left dataarray
        right_da (xr.DataArray): Right DataArray
        dims (Dimension): Dimensions to apply IoU on.
            Defaults to SPACE_DIM.

    Returns:
        xr.DataArray: Table of the computed IoL along the given dims.
    """
    if left_da.dtype != "bool":
        left_da = left_da.astype("int8").astype("bool")
    if right_da.dtype != "bool":
        right_da = right_da.astype("int8").astype("bool")
    return (left_da * right_da).sum(dims) / (1.0 * left_da.sum(dims))


def generic_merge(
    left_da: Optional[xr.DataArray],
    right_da: Optional[xr.DataArray],
) -> xr.DataArray:
    """Merge two DataArrays with a safe mode in case of any given dataarray is None.

    Args:
        left_da (Optional[xr.DataArray]): Left DataArray
        right_da (Optional[xr.DataArray]): Right DataArray

    Returns:
        xr.DataArray: Resulting merged DataArray
    """
    if left_da is None:
        return right_da
    if right_da is None:
        return left_da
    name = left_da.name
    return xr.merge([left_da, right_da])[name]


class GenericArea:
    """
    Class to contain and manipulate combinations of areas.

    Args:
        mask_da (Optional[xr.DataArray]): DataArray containing the mask applied for
            prior risk calculations. Defaults to None.
        alt_min (Optional[int]): Altitude min boundary. Defaults to ALT_MIN.
        alt_max (Optional[int]): Altitude max boundary. Defaults to ALT_MAX.
        spatial_dims (Dimension): Spatial dimensions to apply aggregation
            functions to. Defaults to SPACE_DIM.
    """

    def __init__(
        self,
        mask_da: Optional[xr.DataArray] = None,
        alt_min: Optional[int] = ALT_MIN,
        alt_max: Optional[int] = ALT_MAX,
        spatial_dims: Dimension = SPACE_DIM,
    ):
        """
        Create a generic area object.

        Args:
            mask_da: The mask DataArray.
            alt_min: The minimum altitude.
            alt_max: The maximum altitude.
            spatial_dims: The spatial dimensions.

        """
        self.mask_da: Optional[xr.DataArray] = mask_da
        self.alt_min: int = int(alt_min) if alt_min is not None else ALT_MIN
        self.alt_max: int = int(alt_max) if alt_max is not None else ALT_MAX
        self.spatial_dims: Union[str, Sequence[str]] = (
            spatial_dims if spatial_dims is not None else SPACE_DIM
        )

    @property
    def alt_kwargs(self) -> Dict[str, int]:
        """Property to provide alt_min and alt_max as a mapping to use as keyword
        arguments.
        """
        return {"alt_min": self.alt_min, "alt_max": self.alt_max}

    def intersect(
        self, area_da: xr.DataArray, iou_threshold: float = DEFAULT_IOU
    ) -> Optional[xr.DataArray]:
        """Intersect a given area_da with the corresponding zone in self.mask_da
        if the IoU between the area_da and the mask_da's zones exceeds the given
        iou_threshold.

        Args:
            area_da (xr.DataArray): DataArray containing areas definitions.
            iou_threshold (float, optional): IoU threshold to exceed in order to
                consider two zones as similar. Defaults to None.

        Returns:
            xr.DataArray: New DataArray with intersected zones.
        """
        result = None
        if self.mask_da is None:
            LOGGER.debug("mask is absent")
            return result
        id_mask = self.filter_areas(area_da, self.mask_da)
        temp_area = self.mask_da.sel(id=id_mask) * area_da
        ratio = temp_area.sum(self.spatial_dims) / self.mask_da.sum(self.spatial_dims)
        result = temp_area.sel(id=(ratio > iou_threshold).values)

        result["areaName"] = xr.apply_ufunc(
            lambda x: [rename_alt_min_max(v, **self.alt_kwargs) for v in x],
            self.mask_da.sel(id=result.id)["areaName"],
        )
        return result

    def filter_areas(
        self, area_da: xr.DataArray, areas_list_da: xr.DataArray
    ) -> List[str]:
        """
        This function filters all areas that completely include or are completely
        disjoint from the area being divided. These areas are not interesting.

        Args:
            area_da (dataArray): The area being divided.
            areas_list_da (xr.DataArray): DataArray containing a list of valid areas.
        returns:
            List[str] : List of the ids of the areas "included" in the area.
        """
        squeezed_da = area_da.squeeze()
        product = (areas_list_da * squeezed_da).sum(self.spatial_dims)
        idx = (product >= 1) & (product < squeezed_da.sum(self.spatial_dims))
        return areas_list_da.where(idx, drop=True).id.values.tolist()

    def get_other_altitude_area(self, alt_da: xr.DataArray) -> xr.DataArray:
        """
        This function defines new "altitude zones" (e.g. between 200 and 400 meters).
        These zones can only be used for naming.

        Args:
            alt_da (DataArray): A DataArray of altitude zones.

        Returns:
            xr.DataArray: A DataArray containing the new created zones.
        """

        # Create a copy of the input data array and rename the "id" dimension to "id1".
        area_da2 = copy.deepcopy(alt_da)
        area_da2 = area_da2.rename({"id": "id1"})

        # Calculate the intersection between the two input data arrays.
        dinter = area_da2 * alt_da
        nb_inter = dinter.sum(self.spatial_dims)

        # Create a mask that indicates where the intersection is non-zero, less than the
        # area of either input data array, and less than the sum of the two input data
        # arrays.
        res = (
            (nb_inter > 0)
            * (nb_inter < alt_da.sum(self.spatial_dims))
            * (nb_inter < area_da2.sum(self.spatial_dims))
        )

        # Initialize a list to store the new data arrays.
        l_set = set()
        l_out = []
        name_out = []

        # Iterate over the indices of the mask where the intersection is non-zero.
        for idi in res.id.values:

            # Get the domain data array for the current index.
            domain_da = alt_da.sel(id=idi)

            # Get the list of data arrays for the current index in the second input
            # data array.
            l_area = area_da2.sel(id1=res.sel(id=idi))
            if len(l_area) > 0:
                for area in l_area:
                    id1 = area.id1.values

                    # Check if the current combination of indices has been seen before.
                    ref = (idi, id1)
                    ref_bis = (id1, idi)
                    if ref not in l_set and ref_bis not in l_set:

                        # Get the name of the new zone.
                        name_inter = self.rename_inter(
                            domain_da.areaName.item(),
                            area.areaName.tolist(),
                        )

                        # Add the current combination of indices to the set of seen
                        # combinations.
                        l_set.add(ref)

                        # Create a new data array for the new zone
                        intersection = (
                            dinter.sel(id=idi)
                            .sel(id1=id1)
                            .drop_vars(["id", "id1", "areaType"])
                        )
                        intersection = intersection.expand_dims("id").assign_coords(
                            id=[f"inter_{str(idi)}_{str(id1)}"]
                        )
                        intersection["areaName"] = (("id"), name_inter)
                        intersection["areaType"] = (
                            ("id"),
                            ["Altitude"],
                        )

                        # Add the new data array to the list of new data arrays.
                        l_out.append(intersection)
                        name_out.append(name_inter)

        # On regarde ensuite les complémentaires "au sein de la zone"
        # Par ex > 1000 dans la zone >700 => Entre 700 et 1000
        comp_area_da = alt_da.copy() - (area_da2 > 0)
        d_comp = comp_area_da.where(comp_area_da > 0)
        nb_comp = d_comp.sum(self.spatial_dims)
        res = (
            (nb_comp > 0)
            * (nb_comp < alt_da.sum(self.spatial_dims))
            * (nb_comp < area_da2.sum(self.spatial_dims))
        )
        for idi in res.id.values:
            domain_da = alt_da.sel(id=idi)
            l_area = area_da2.sel(id1=res.sel(id=idi))
            if len(l_area) > 0:
                for area in l_area:
                    id1 = area.id1.values
                    ref = (idi, id1)
                    ref_bis = (id1, idi)
                    if ref not in l_set and ref_bis not in l_set:
                        name_comp = self.rename_difference(
                            str(domain_da.areaName.values),
                            [str(area.areaName.values)],
                        )
                        if name_comp not in name_out:
                            l_set.add(ref)
                            difference = (
                                d_comp.sel(id=idi)
                                .sel(id1=id1)
                                .drop_vars(["id", "id1", "areaType"])
                            )
                            difference = difference.expand_dims("id").assign_coords(
                                id=[f"diff_{str(idi)}_{str(id1)}"]
                            )
                            difference["areaName"] = (("id"), name_comp)
                            difference["areaType"] = (
                                ("id"),
                                ["Altitude"],
                            )
                            l_out.append(difference)
                            name_out.append(name_comp)
        name = alt_da.name

        # Merge the list of new data arrays into a single data array.
        dout = xr.merge(l_out)[name]
        return dout

    def rename_inter(
        self, domain_name: str, area_name: Union[str, List[str]]
    ) -> Union[str, List[str]]:
        """Rename the area that is the intersection between a given domain_name
        and a sub_area_name.

        !Warning: We suppose that the sub_area is included in the domain. The goal of
        that method is to provide the corresponding name of such an intersection.

        For instances:
        >> gen = GenericArea(..., alt_min=500, alt_max=2000)
        >> gen.rename_inter('en Isère', ['à Grenoble', 'entre 1000 m et 1500 m',
        ..     'entre 1000 m et 2000 m']
        .. )
        ['à Grenoble', 'entre 1000 m et 1500 m', 'au-dessus de 1000 m']
        >> gen.rename_inter('au-dessus de 1500 m', 'sur le massif de Belledonne')
        'sur le massif de Belledonne au-dessus de 1500 m'
        >> gen.rename_inter('entre 1500 m et 2000 m', 'sur le massif de Belledonne')
        'sur le massif de Belledonne au-dessus de 1500 m'
        >> gen.rename_inter('entre 1000 m et 1800 m', 'au-dessus de 1500 m')
        'entre 1500 m et 1800 m'
        >> gen.rename_inter('entre 1000 m et 2000 m', 'au-dessus de 1500 m')
        'au-dessus de 1500 m'

        Args:
            domain_name (str): Name of the area considered as the domain.
                The concept of domain is important here because we will not rephrase the
                domain's name if not necessary (contrary to the sub_area).
            area_name (Union[str, List[str]]): Name of the area(s) we will intersect
                with the domain.

        Returns:
            Union[str, List[str]]: Name(s) of the intersection between the area(s)
            and the domain.
        """
        if isinstance(area_name, List):
            return [self.rename_inter(domain_name, sub_area) for sub_area in area_name]

        domain_interval = AltitudeInterval.from_str(domain_name)
        sub_area_interval = AltitudeInterval.from_str(area_name)
        if bool(domain_interval):
            if bool(sub_area_interval):
                return (domain_interval & sub_area_interval).name(**self.alt_kwargs)
            return f"{area_name} {domain_interval.name(**self.alt_kwargs)}"
        if bool(sub_area_interval):
            return sub_area_interval.name(**self.alt_kwargs)
        return area_name

    def rename_difference(
        self, domain_name: str, area_name: Union[str, List[str]]
    ) -> Union[str, List[str]]:
        """Rename the area that is the difference between a given domain_name
        and area names.

        !Warning: We suppose that the sub_area is included in the domain. The goal of
        that method is to provide the corresponding name of such a difference.

        For instances:
        >>> gen = GenericArea(..., alt_min=500, alt_max=2000)
        >>> gen.rename_difference('en Isère', ['à Grenoble', 'entre 1000 m et 1500',
        ...     'entre 1000 m et 2000 m']
        ... )
        ['comp_à Grenoble', 'en dessous de 1000 m et au-dessus de 1500 m', 'en dessous
            de 1000 m']
        >>> gen.rename_difference(
        ...     'au-dessus de 1500 m', 'sur le massif de Belledonne'
        ... )
        'au-dessus de 1500 m sauf sur le massif de Belledonne']
        >>> gen.rename_difference(
        ...     'entre 1500 m et 2000 m', 'sur le massif de Belledonne',
        ... )
        'au-dessus de 1500 m sauf sur le massif de Belledonne'
        >>> gen.rename_difference(
        ...    'entre 1000 m et 1800 m', 'au-dessus de 1500 m'
        ... )
        'entre 1000 m et 1500 m'
        >>> gen.rename_difference(
        ...    'entre 500 m et 1800 m', 'au-dessus de 1500 m'
        ... )
        'en dessous de 1500 m'

        Args:
            domain_name (str): Name of the area considered as the domain.
                The concept of domain is important here because we will not rephrase the
                domain's name if not necessary (contrary to the sub_area).
            area_name (Union[str, List[str]]): Name of the area(s) we will intersect
                with the domain.

        Returns:
            Union[str,Iterable[str]]: Name(s) of the difference between the area(s)
            and the domain.
        """
        if isinstance(area_name, List):
            return [
                self.rename_difference(domain_name, sub_area) for sub_area in area_name
            ]

        domain_interval = AltitudeInterval.from_str(domain_name)
        sub_area_interval = AltitudeInterval.from_str(area_name)
        if bool(domain_interval):
            if bool(sub_area_interval):
                return domain_interval.difference(sub_area_interval).name(
                    **self.alt_kwargs
                )
            return (
                f"{domain_interval.name(**self.alt_kwargs)}"
                f" {LANGUAGE.sauf} {area_name}"
            )
        if bool(sub_area_interval):
            return f"{(~sub_area_interval).name(**self.alt_kwargs)}"
        return f"comp_{area_name}"

    @staticmethod
    def best_complementary(
        comp_area_da: xr.DataArray,
        full_list_da: xr.DataArray,
        iou_threshold: float = DEFAULT_IOU,
    ) -> Tuple[xr.DataArray, xr.DataArray, xr.DataArray]:
        """
        This function sorts the complementary zones by their similarity to the given
        complementary zone. The altitude zones are sorted separately from the other
        zones.

        Args:
            comp_area_da (xr.DataArray): The complementary zone whose name we need to
                find.
            full_list_da (xr.DataArray): The list of zones from which we can choose.
            iou_threshold (float, optional): The intersection-over-union threshold to
                use for sorting the zones. Defaults to `DEFAULT_IOU`.

        Returns:
            (xr.DataArray, xr.DataArray, xr.DataArray):
                * `is_over_threshold` is a boolean array indicating whether each zone
                    is above the intersection-over-union threshold.
                * `ids_of_maxs` is an array of integers indicating the IDs of the zones
                    with the highest similarity to the given complementary zone.
                * `is_altitude` is a boolean array indicating whether each zone is an
                    altitude zone.
        """
        # On va trier les zones : on va mettre les zones d'altitude d'un côté et
        # les autres zones de l'autre.

        if (
            hasattr(full_list_da, "areaType")
            and (full_list_da["areaType"] == "Altitude").sum().values > 0
        ):
            idx = full_list_da["areaType"] == "Altitude"
            alt_area_da = full_list_da.sel(id=idx)
            idx_other = set(full_list_da.id.values).difference(
                set(alt_area_da.id.values)
            )
            other_area_da = full_list_da.sel(id=list(idx_other))
            iou_alt = compute_IoU(comp_area_da, alt_area_da)
            # Max, est-on superieur au seuil et nom.
            m_alt = iou_alt.max("id")
            r_alt = m_alt > DEFAULT_IOU_ALT
            a_alt = iou_alt.argmax("id")
            if len(list(idx_other)) > 0:
                iou_other = compute_IoU(comp_area_da, other_area_da)
                # Donne le max de l'IoU
                m_other = iou_other.max("id")
                # Ratio et argmax (donne le ratio et le nom )
                r_other = m_other > iou_threshold
                a_other = iou_other.argmax("id")
                # Si on a un seul ratio on prend celui là et la zone correspondante.
                # si on a plusieurs ratio_ok il faut prendre le meilleur des deux et
                # recupérer l'id correspondant
                ratio = r_alt + r_other
                ids = (
                    r_alt
                    * ((1 - r_other) + r_other * (m_alt > m_other))
                    * alt_area_da.isel(id=a_alt).id.values
                    + r_other
                    * ((1 - r_alt) + r_alt * (m_other >= m_alt))
                    * other_area_da.isel(id=a_other).id.values
                )
                alti_field = r_alt * ((1 - r_other) + r_other * (m_alt > m_other))
            else:
                ratio = r_alt
                ids = r_alt * alt_area_da.isel(id=a_alt).id.values
                alti_field = r_alt
        else:
            iou = compute_IoU(comp_area_da, full_list_da)
            iou_max = iou.max("id")
            # Permet de savoir à quelle zone on l'associe.
            a_max = iou.argmax("id")
            ids = full_list_da.isel(id=a_max).id
            ratio = iou_max > iou_threshold
            alti_field = ratio * False
        return ratio, ids, alti_field

    def difference(
        self, area_da: xr.DataArray, full_list_da: Optional[xr.DataArray]
    ) -> Optional[xr.DataArray]:
        """
        Compute the difference between the areas in `self.mask_da` and the input
        `area_da`. If the corresponding area IoU between complementary and original
        area (in the list) is greater than a threshold, we keep it. Otherwise, we
        discard it.

        We also rename this area according to the "closest" area in the full list.

        Args:
            area_da (xr.DataArray): DataArray containing the areas to substract to
                `self.mask_da`.

        Returns:
            xr.DataArray: the resulting difference of `self.mask_da` and `area_da`.
        """
        result = None
        if self.mask_da is None:
            LOGGER.debug("mask is absent")
            return result
        id_full = self.filter_areas(area_da, full_list_da)
        # Option pour ne pas avoir un complementaire qui porte le meme nom que le
        # 'domaine'.
        if len(id_full) == 0:
            LOGGER.warning(
                f"Apres contrôle, pas de zone disponible pour {area_da.areaName.values}"
            )
            return None
        id_mask = self.filter_areas(area_da, self.mask_da)
        full_list_da = full_list_da.sel(id=id_full)
        comp_area_da = (
            area_da.squeeze() - (self.mask_da.sel(id=id_mask) > 0)
        ) * area_da
        comp_area_da = comp_area_da.wheretype.f32(comp_area_da > 0)

        # On change l'identifiant de nom
        comp_area_da = comp_area_da.rename({"id": "id1"})
        try:
            ratio, ids, _ = self.best_complementary(comp_area_da, full_list_da)
        except ValueError as e:
            LOGGER.error(f"Full list of possibility is {full_list_da}")
            LOGGER.error(f"The input area_da is {area_da}")
            LOGGER.error(
                f"An error has happend in area_algebra. Comp_area is {comp_area_da}"
            )
            raise e
        # On regarde quels sont les ids des zones complémentaire qu'on va conserver
        # result = comp_area_da.sel(id1=ratio)
        result = comp_area_da.sel(id1=ratio)
        if ratio.sum() >= 1:
            # On va maintenant essayer de renommer.
            # areaNames = []
            areaBis = []
            areaType = []
            for idi in ids.sel(id1=ratio):
                areaBis.append(
                    rename_alt_min_max(
                        str(full_list_da.sel(id=idi.values)["areaName"].values),
                        **self.alt_kwargs,
                    )
                )
                areaType.append(str(full_list_da.sel(id=idi.values)["areaType"].values))
            result["areaName"] = (("id1"), areaBis)
            # la ligne suivante a été insérée à l'état de commentaire vers 05/2021
            # pourtant elle est nécessaire au bon traitement du sous zonage car
            # areaType sert de filtre pour sélectionner les zones d'altitude
            result["areaType"] = (("id1"), areaType)
            result = result.rename({"id1": "id"})
        else:
            # On a ici aucun résultat
            result = None
        return result


class AltArea(GenericArea):
    """Permet de générer un objet GenericArea à partir de données
    d'altitude
    """

    def restrict_to(
        self,
        area_da: xr.DataArray,
        other_areas_da: xr.Dataset,
    ) -> xr.Dataset:
        """Restreint la liste d'areas donnée dans other_areas_da à un intervale
        d'altitude donné par area_da (si area_da contient une zone définie par altitude)

        Args:
            area_da (xr.DataArray): DataArray contenant la zone par altitude pour
                restreindre.
            other_areas_da (xr.Dataset): Zones à selectionner.

        Returns:
            xr.Dataset: Dataset contenant des zones préselectionnées.
        """
        area_interval = AltitudeInterval.from_str(area_da.areaName.values)
        drop_ids = []
        if bool(area_interval):
            # given area is altitude defined
            for other_name_da in other_areas_da.areaName:
                other_interval = AltitudeInterval.from_str(other_name_da.values)
                if bool(other_interval) and not other_interval.is_sub_interval(
                    area_interval
                ):
                    drop_ids.append(other_name_da.id.values)
        if len(drop_ids) == 0:
            # returns a copy of the other_areas_da
            return other_areas_da.sel(id=other_areas_da.id)
        return other_areas_da.sel(
            id=list(set(other_areas_da.id.values).difference(drop_ids))
        )

    def intersect(
        self, area_da: xr.DataArray, iou_threshold: float = DEFAULT_IOU
    ) -> Optional[xr.DataArray]:
        """Calcul de l'intersection entre une zone et la liste de zone d'altitude.
            Seul les zones "correctes" sont retournées

        Args:
            area_da (dataArray): Une zone spécifique

        Returns:
            [none or dataArray]:
                Une liste des zones qui ont une intersection "correcte"
                avec la zone en question.
                Ces zones ont été restreints à la zone en question.
                Elles ont potentiellement été renommés
        """
        result = None
        if self.mask_da is None:
            return result
        if area_da["areaType"] == "Altitude":
            id_mask = self.filter_areas(area_da, self.mask_da)
            temp_area = self.mask_da.sel(id=id_mask) * area_da.copy()
            # On ne considere que les zones qui couvrent au moins 5% de l'aire
            idx = temp_area.sum(self.spatial_dims) > 0.05 * area_da.sum(
                self.spatial_dims
            )
            result = temp_area.isel(id=idx.values)
            l_name = self.mask_da.sel(id=result.id)["areaName"].values
            result["areaName"] = (
                "id",
                self.rename_inter(area_da.areaName.item(), l_name.tolist()),
            )
            # On va encore restreindre aux cas logiques. On ne veut pas avoir >250 si
            # le domaine est >300.
            result = self.restrict_to(area_da, result)
        else:
            result = super().intersect(area_da, iou_threshold=iou_threshold)
        return result

    def difference(
        self, area_da: xr.DataArray, full_list_da: Optional[xr.DataArray]
    ) -> Optional[xr.DataArray]:
        """
        On souhaite avoir le complémentaire de chaque zone à l'intérieur
        du domaine D (i-e D - area_da).

        Si la zone d'entrée est une zone d'altitude, on sait la nommer.
        Si ça n'en est pas une, on passe par la méthode générique.
        On vérifiera (dans un second temps) si on peut nommer cette zone.

        Args:
            area_da (dataArray): Une zone spécifique

        Returns:
            [none or dataArray]:
                Une liste des zones qui ont une intersection "correcte"
                avec la zone en question.
                Ces zones ont été restreints à la zone en question.
                Elles ont potentiellement été renommés
        """
        result = None
        if self.mask_da is None:
            return result
        if area_da["areaType"] == "Altitude":
            id_mask = self.filter_areas(area_da, self.mask_da)
            comp_area_da = area_da.copy() - (self.mask_da.sel(id=id_mask) > 0)
            comp_area_da = comp_area_da.where(comp_area_da > 0)
            # On ne considere que les zones qui couvrent au moins 5% de l'aire
            idx = comp_area_da.sum(self.spatial_dims) > 0.05 * area_da.sum(
                self.spatial_dims
            )
            result = comp_area_da.isel(id=idx.values)
            l_name = self.mask_da.sel(id=result.id)["areaName"].values
            result["areaName"] = (
                "id",
                self.rename_difference(area_da.areaName.item(), l_name.tolist()),
            )
        else:
            result = super().difference(area_da, full_list_da)
        return result


class RiskArea:
    """Class permetant d'initialiser les zones descriptives valables (et leurs noms)
    pour les confronter au risque préalablement calculé.

    Args:
        full_list_da (Optional[xr.DataArray]): DataArray contenant le risque appliqué à
            toutes les zones descriptives. Defaults to None.
        iou_threshold (Optional[float]): Threshold of IoU to use to consider two zones
            as sufficiently similar. Defaults to DEFAULT_IOU.
        alt_min (Optional[int]): Altitude min boundary. Defaults to ALT_MIN.
        alt_max (Optional[int]): Altitude max boundary. Defaults to ALT_MAX.
        spatial_dims (Dimension): Spatial dimensions to apply aggregation
            functions to. Defaults to SPACE_DIM.
    """

    def __init__(
        self,
        full_list_da: Optional[xr.DataArray],
        alt_min: Optional[int] = ALT_MIN,
        alt_max: Optional[int] = ALT_MAX,
        spatial_dims: Dimension = SPACE_DIM,
    ):
        self.full_list_da: Optional[xr.DataArray] = full_list_da
        self.alt_min: int = alt_min if alt_min is not None else ALT_MIN
        self.alt_max: int = alt_max if alt_max is not None else ALT_MAX
        self.spatial_dims = spatial_dims if spatial_dims is not None else SPACE_DIM

        if hasattr(full_list_da, "areaType"):
            # On va récupérer les zones qui sont des zones d'altitudes
            idx = full_list_da["areaType"] == "Altitude"

            alt_da = full_list_da.sel(id=idx)
            idx_other = set(full_list_da.id.values).difference(alt_da.id.values)
            other_da = full_list_da.sel(id=list(idx_other))
            self.alt_area_da = AltArea(
                mask_da=alt_da,
                alt_min=self.alt_min,
                alt_max=self.alt_max,
                spatial_dims=self.spatial_dims,
            )
            self.other_area_da = GenericArea(
                mask_da=other_da,
                alt_min=self.alt_min,
                alt_max=self.alt_max,
                spatial_dims=self.spatial_dims,
            )
        else:
            self.alt_area_da = AltArea(
                alt_min=self.alt_min,
                alt_max=self.alt_max,
                spatial_dims=self.spatial_dims,
            )
            self.other_area_da = GenericArea(
                mask_da=self.full_list_da,
                alt_min=self.alt_min,
                alt_max=self.alt_max,
                spatial_dims=self.spatial_dims,
            )

    def get_possibilities(
        self, area_da: xr.DataArray
    ) -> Tuple[Optional[xr.DataArray], Optional[xr.DataArray]]:
        """
        Retourne toute les zones qui sont possibles pour cette zone.
        La réponse peu dépendre du type de zone en entrée.

        1. Si la zone est une zone d'altitude, on retourne
            - Toutes les zones d'altitudes qui ont une intersection non nulle
            - Toutes les autres zones qui sont au moins à 'min_percent' dans la zone
                et dont on peut nommer le complémentaire.
        2. Sinon
            - Toutes les zones qui sont au moins à 'min_percent" dans la zone
                et dont on peut nommer le complémentaire.

        Cette fonction peut évoluer en fonction

        Args:
            area_da (xr.DataArray): Une dataArray contenant une unique zone

        Returns:
            Tuple[xr.DataArray, xr.DataArray]:
                * DataArray contenant les intersections
                * DataArray contenant les differences
        """
        pos_inter_da = self.intersect(area_da)
        pos_comp_da = self.difference(area_da)
        if pos_inter_da is not None and pos_comp_da is not None:
            common_id = set(pos_inter_da.id.values).intersection(pos_comp_da.id.values)
            if common_id != set():
                return (
                    pos_inter_da.sel(id=list(common_id)),
                    pos_comp_da.sel(id=list(common_id)),
                )
            LOGGER.debug("Pas d'id en commum")
            return None, None
        LOGGER.debug("Aucune zone dans l'intersection ou le complementaire")
        return None, None

    def intersect(self, area_da: xr.DataArray) -> xr.DataArray:
        """Retourne l'intersection entre les zones de self.alt_area_da et
        self.other_area_da avec la zone contenue dans area_da.

        Args:
            area_da (xr.DataArray): Zone a intersecter.

        Returns:
            xr.DataArray: DataArray contenant l'ensemble des zones qui intersecte
                area_da.
        """
        alt_intersect_da = self.alt_area_da.intersect(area_da)
        other_intersect_da = self.other_area_da.intersect(area_da)
        return generic_merge(alt_intersect_da, other_intersect_da)

    def difference(self, area_da: xr.DataArray) -> xr.DataArray:
        """Retourne la différence entre les zones de self.alt_area_da et self.other_da
        avec la zone contenue dans area_da.

        Args:
            area_da (xr.DataArray): Zone a soustraire (i.e. trouver des complémentaires)

        Returns:
            xr.DataArray: DataArray contenant l'ensemble des zones complémentaires
                de area_da.
        """
        alt_diff_da = self.alt_area_da.difference(area_da, self.full_list_da)
        other_diff_da = self.other_area_da.difference(area_da, self.full_list_da)
        return generic_merge(alt_diff_da, other_diff_da)

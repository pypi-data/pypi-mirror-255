"""
This module is for the management of 3x3 tables.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Tuple

import numpy as np
from dateutil.parser import ParserError

import mfire.utils.mfxarray as xr
from mfire.localisation import SpatialIngredient, compute_IoU, rename_alt_min_max
from mfire.settings import ALT_MAX, ALT_MIN, get_logger
from mfire.text.period_describer import PeriodDescriber
from mfire.utils.calc import bin_to_int
from mfire.utils.date import Datetime, Period
from mfire.utils.json_utils import JsonFile
from mfire.utils.string_utils import concatenate_string

# Logging
LOGGER = get_logger(name="table.mod", bind="table")

xr.set_options(keep_attrs=True)


class SummarizedTable:
    """
    Gere les tableaux résumant la situation.
    """

    _nc_table = "input_table.nc"
    _spatial_base_name = "SpatialIngredient"
    _json_config = "summarized_table_config.json"

    def __init__(
        self,
        da: xr.DataArray,
        request_time: Datetime,
        full_period: Period,
        spatial_ingredient: Optional[SpatialIngredient] = None,
    ):
        """
        Args:
            da (DataArray): A 3 period dataArray
            request_time (Datetime) : production datetime
            full_period (Period) : periode couverte par le bulletin
                Permettrait de mettre en relief le tableau.
        """
        self.input_table = da
        self.spatial_ingredient = spatial_ingredient
        self.request_time = request_time
        self.full_period = full_period
        # ------------------------------------

        self.working_table = da.copy()

        self._raw_table = []
        self._unique_table = xr.DataArray()
        self.define_unique_table()

    @property
    def unique_table(self) -> xr.DataArray:
        """Return table. The table is sorted and in reduced form
        Returns:
            [dataArray]: The table
        """
        return self._unique_table

    @property
    def unique_name(self) -> str:
        """Return the name of the reduced form table

        Returns:
            [str]: The table name
        """
        table_set = set(self._raw_table)
        base = [next(k for k in table_set if isinstance(k, str))]
        nums = sorted(str(int(k)) for k in table_set if not isinstance(k, str))
        return f"P{'_'.join(base + nums)}"

    @property
    def raw_table(self) -> list:
        """Return reduced table as a list

        Returns:
            [list]: The list contain  the number of period
                    as well as the description of each table line.
        """
        return self._raw_table

    @property
    def encoded_table(self) -> Tuple:
        """Returns the 2-D binary encoded DataArray into a tuple of integer along the
        dimension id.

        Raises:
            ValueError: raised if values in the table_da DataArray are not convertible
                to int.

        Returns:
            Tuple: Encoded table.
        """
        try:
            return tuple(
                [
                    bin_to_int(self.working_table.sel({"id": v}).values)
                    for v in self.working_table["id"]
                ]
            )
        except ValueError as excpt:
            LOGGER.error(
                "Failed to encode table along given id. Exception Raised.",
                table_da=self.working_table,
            )
            raise excpt

    @staticmethod
    def representative_area_properties(
        area_list: xr.DataArray,
        area_possibilities: xr.DataArray,
        domain: xr.DataArray = None,
        alt_min: Optional[int] = ALT_MIN,
        alt_max: Optional[int] = ALT_MAX,
    ) -> Tuple[str, str]:
        """
        This method gets the representative area properties, which are the id and
        probability of the area with the maximum probability in the specified
        altitude range. If there are no ideal candidates, we will take care of renaming
        (roughly) certain properties.

        Args:
            area_list: xr.DataArray
                The list of areas.
            area_possibilities: xr.DataArray
                The possibilities of the areas.
            domain: xr.DataArray = None
                The domain of the areas.
            alt_min: Optional[int] = ALT_MIN
                The minimum altitude.
            alt_max: Optional[int] = ALT_MAX
                The maximum altitude.

        Returns:
            Tuple[str, str]
                The representative area properties.
        """

        # Compute the IoU between each area and the sum of the other areas.
        area_sum = area_list.sum("id", min_count=1)

        # Concatenation of the names of the areas
        list_name = area_list["areaName"].values.astype(str)
        list_name.sort()
        area_name = concatenate_string(list_name)

        area_type = np.unique(area_list.areaType)
        area_type = area_type[0] if len(area_type) == 1 else "No"

        # Rename the area name to include the minimum and maximum altitudes.
        if area_type == "Altitude":
            area_name = rename_alt_min_max(
                area_name=area_name,
                alt_min=alt_min,
                alt_max=alt_max,
            )

        # If the domain is not None, then also check the IoU between the sum of the
        # areas and the domain.
        if domain is not None:
            IoU = compute_IoU(area_sum, domain)
            LOGGER.debug(f"IoU for domain is {IoU.values}")
            if IoU > 0.98:
                # If the IoU is greater than 0.98, then use the name and type of the
                # domain.
                area_name = domain["areaName"].values
                area_type = "domain"

        LOGGER.debug(f"Name : {str(area_name)}, Type: {str(area_type)}")
        return str(area_name), str(area_type)

    def save(self, path: Path):
        """Save the summarized table and the spatial ingredient.

        Args:
            path: The path to the output directory.
        """
        # Save the summarized table to a NetCDF file.
        LOGGER.info(f"Saving  summarized table to {path / self._nc_table}")
        self.input_table.to_netcdf(path / self._nc_table)

        # Save the spatial ingredient to a file.
        if self.spatial_ingredient is not None:
            self.spatial_ingredient.auto_save(path / self._spatial_base_name)

        # Save the request time and full period to a JSON file.
        dout = {
            "request_time": self.request_time,
            "full_period": self.full_period.to_json,
        }
        JsonFile(path / self._json_config).dump(dout)

    @classmethod
    def load(cls, path: Path) -> SummarizedTable:
        """Load the summarized table and the spatial ingredient from a directory.

        Args:
            path: The path to the output directory.

        Returns:
            The summarized table.
        """
        # Open the summarized table NetCDF file.
        input_table = xr.open_dataarray(path / cls._nc_table).load()

        # If the spatial ingredient file exists, open it.
        if (path / cls._spatial_base_name).exists():
            spatial_ingredient = SpatialIngredient.load(path / cls._spatial_base_name)
        else:
            spatial_ingredient = None

        # Load the request time and full period from the JSON file.
        data = JsonFile(path / cls._json_config).load()
        request_time = data["request_time"]
        full_period = Period(**data["full_period"])

        # Create a new `SummarizedTable` object.
        return cls(input_table, request_time, full_period, spatial_ingredient)

    def define_unique_table(self) -> None:
        """
        This function perform operation on the input table.
         - Squeeze empty period
         - merge similar period
         - Order and merge area
        This is done while keeping information on AreaName and on PeriodName.
        It enables to define the "unique_table" and the unique_name
        """
        self._squeeze_empty_period()
        self._merge_similar_period()
        self._merge_period_with_same_name()
        self._merge_similar_period()

        # Il va falloir maintenant permuter les lignes
        raw_table = list(self.encoded_table)
        self.working_table["raw"] = (("id"), raw_table)

        raw_table.insert(0, str(int(self.working_table.period.size)))
        self._raw_table = raw_table
        # On va permuter et fusionner les lignes en fonction des résultats du tuple
        # On n'a pas besoin de redefinir le nom unique apres
        # (on sait avant de l'envoyer au charbon qu'il y aura fusion)
        dout = self.order_and_merge_area()
        self._unique_table = dout[self.input_table.name]

    def _squeeze_empty_period(self) -> None:
        """
        Supprime les périodes vides en début et fin de talbeau.
        """
        i = 0
        squeeze_list = []
        while self.working_table.isel(period=[i]).sum().values == 0:
            squeeze_list.append(i)
            i += 1
        i = self.working_table.period.size - 1
        while self.working_table.isel(period=[i]).sum().values == 0:
            squeeze_list.append(i)
            i += -1
        select = set([i for i in range(self.working_table.period.size)])
        to_select = sorted(select.difference(set(squeeze_list)))
        self.working_table = self.working_table.isel(period=to_select)

    def _merge_similar_period(self) -> None:
        """
        Merge similar period.
        Two period are similar if they are adjacent and risk values are the same.

        This function should work for any number of period.
        """
        index_to_remove = []
        period_name = [self.working_table.period.isel(period=0).values]
        if self.working_table.period.size > 0:
            for p in range(1, self.working_table.period.size):
                if (
                    self.working_table.isel(period=[p]).values
                    == self.working_table.isel(period=[p - 1]).values
                ).all():
                    index_to_remove.append(p)
                    # Mettre un nom de period en adequation.
                    period_name[-1] = (
                        str(period_name[-1])
                        + "_+_"
                        + str(self.working_table.isel(period=[p])["period"].values[0])
                    )
                else:
                    period_name.append(self.working_table.period.isel(period=p).values)

        if index_to_remove:
            index = set(list(range(self.working_table.period.size)))
            index = index.difference(set(index_to_remove))
            keep_list = sorted(index)
            self.working_table = self.working_table.isel(period=keep_list)
            self.working_table["period"] = period_name

    def _merge_period_with_same_name(self):
        """Merge periods with the same name."""
        array_name = self.working_table.name
        period_describer = PeriodDescriber(self.request_time)
        the_names = []
        for period in self.working_table["period"].values:
            time_list = period.split("_to_")
            try:
                period_obj = Period(time_list[0], time_list[-1])
                LOGGER.debug(
                    f"Period = {period_obj} "
                    f"({period_describer.describe(period_obj)})"
                )
            except ParserError:
                LOGGER.warning(
                    f"At least one period value is not a datetime {period}. "
                    "We will not merge period by name."
                )
                return None
            the_names += [period_describer.describe(period_obj)]

        self.working_table["period_name"] = (("period"), the_names)
        # Maintenant on va merger
        # Pour cela on va selectionner les periodes ayant le même nom et on les merge.
        # On suppose que des périodes portent le même nom seulement si elles sont
        # consécutives.
        if len(set(the_names)) != len(the_names):
            LOGGER.info(
                "Différentes périodes ont le même nom. "
                "On va merger ces périodes (en prenant le pire des risques)."
            )
            tmp_list = []
            for pname in set(the_names):
                table_to_reduce = self.working_table.where(
                    self.working_table.period_name == pname, drop=True
                )
                if table_to_reduce.period.size > 1:
                    reduced_table = table_to_reduce.max("period")
                    first_period = str(
                        table_to_reduce["period"].isel(period=0).values
                    ).split("_to_")
                    last_period = str(
                        table_to_reduce["period"].isel(period=-1).values
                    ).split("_to_")
                    reduced_table["period"] = first_period[0] + "_to_" + last_period[-1]
                    reduced_table = reduced_table.expand_dims("period")
                    tmp_list += [reduced_table]
                else:
                    tmp_list += [table_to_reduce]
            self.working_table = xr.merge(tmp_list)[array_name]
        if "period_name" in self.working_table.coords:
            self.working_table = self.working_table.drop_vars("period_name")

    def merge_zones(
        self,
        da: xr.DataArray,
        alt_min: Optional[int] = ALT_MIN,
        alt_max: Optional[int] = ALT_MAX,
    ) -> xr.DataArray:
        """
        Devrait fonctionner avec n'importe quel nombre de zones
        Merge les zones similaires.
        Conserve les autres variables dépendant de l'identificateur de zones

        Devrait être appelé depuis l'exterieur pour merger des zones du talbeau ?

        Args :
            da (DataArray)
        """
        if da["id"].size > 1:
            # Determination du nouvel id
            area_id = "_+_".join(da["id"].values.astype(str))
            dout = da.max("id").expand_dims("id").assign_coords({"id": [area_id]})
            # On va regarder les autres coordonnées.
            # On merge de manière pas bête les noms seulement si on a un
            # spatial_ingredient.
            if "areaName" in da.coords and self.spatial_ingredient is not None:
                ids_set = {v for ids in da.id.values for v in ids.split("_+_")}
                sel_ids_set = ids_set.intersection(
                    self.spatial_ingredient.localised_area.id.values
                )
                if sel_ids_set != ids_set:
                    LOGGER.warning(
                        "Ids non présents dans localised_area",
                        missing_ids=list(ids_set.difference(sel_ids_set)),
                        ids_set=list(ids_set),
                        id_localised=self.spatial_ingredient.localised_area.id.values,
                    )
                (area_name, area_type) = self.representative_area_properties(
                    self.spatial_ingredient.localised_area.sel(id=list(sel_ids_set)),
                    self.spatial_ingredient.full_area_list,
                    domain=self.spatial_ingredient.domain,
                    alt_min=alt_min,
                    alt_max=alt_max,
                )
                dout["areaName"] = ("id", [str(area_name)])
                dout["areaType"] = ("id", [area_type])
                LOGGER.debug(f"areaName {area_name} ")
            elif "areaName" in da.coords:
                area_type = np.unique(da.areaType.values)
                area_type = area_type[0] if len(area_type) == 1 else "No"

                # Rename the area name to include the minimum and maximum altitudes.
                area_name = da["areaName"].values.astype(str)
                if area_type == "Altitude":
                    area_name = rename_alt_min_max(
                        area_name=area_name,
                        alt_min=alt_min,
                        alt_max=alt_max,
                    )

                dout["areaName"] = ("id", ["_+_".join(area_name)])
                dout["areaType"] = (("id"), ["mergedArea"])

        else:
            dout = da
            if "areaName" in da.coords:
                area_name = np.unique(da.areaName.values)[0]
                if "areaType" in da.coords and da.areaType == "Altitude":
                    area_name = rename_alt_min_max(
                        area_name=area_name,
                        alt_min=alt_min,
                        alt_max=alt_max,
                    )
                dout["areaName"] = (
                    "id",
                    [area_name],
                )
        return dout

    def order_and_merge_area(self) -> xr.DataArray:
        """
        Ordonne le dataArray pour être en phase avec le modèle unique.
        Fusionne aussi les zones similaires.
        Returns :
           Le dataArray avec les zones mergées et permutées.
        """
        table = sorted(set(self.working_table["raw"].values))
        final_list = []
        area_list = []  # Permet d'etre sur de l'ordre apres le merge.
        for elt in table:
            db = self.working_table.sel({"id": (self.working_table["raw"] == elt)})
            dtmp = self.merge_zones(db.drop_vars("raw"))
            area = dtmp["id"].values
            if isinstance(area, Iterable):
                area_list.append(area[0])
            else:
                area_list.append(area)
            final_list.append(dtmp)
        dout = xr.merge(final_list).sel({"id": area_list})
        if "areaName" in dout.coords:
            dout["areaName"] = dout["areaName"].astype(str)
        return dout

    def update_unique_table(self, id_list: list):
        """Updates the self.unique_table by selecting given ids.

        Args:
            id_list (list): List of ids to select in the self.unique_table.
        """
        LOGGER.debug(f"Unique_name before {self.unique_name}")
        area_to_merge = self.working_table.sel(id=id_list)
        merged_area = self.merge_zones(area_to_merge)
        unmerged_id = [
            idi for idi in self.working_table.id.values if idi not in id_list
        ]
        if unmerged_id != []:
            unmerged_area = self.working_table.sel(id=unmerged_id)
            self.working_table = xr.merge(
                [
                    merged_area.drop_vars("raw", errors="ignore"),
                    unmerged_area.drop_vars("raw", errors="ignore"),
                ]
            )["elt"]
        else:
            self.working_table = merged_area.drop_vars("raw")
        self.define_unique_table()
        LOGGER.debug(f"Unique_name after {self.unique_name}")

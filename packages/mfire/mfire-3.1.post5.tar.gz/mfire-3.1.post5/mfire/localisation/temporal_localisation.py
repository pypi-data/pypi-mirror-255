from typing import Optional, Tuple, Union

import numpy as np

import mfire.utils.mfxarray as xr
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="temporal_localisation.mod", bind="temporal_localisation")

xr.set_options(keep_attrs=True)


class TemporalLocalisation:
    """
    Class for temporal localisation of a DataArray.

    Attributes:
        da: xr.DataArray
            The DataArray after localisation.
        time_dimension: str
            The name of the time dimension in the DataArray.
        area_dimension: str
            The name of the area dimension in the DataArray.
        trim_period: bool
            Whether to trim the DataArray to the period of interest.
    """

    def __init__(
        self,
        da: xr.DataArray,
        time_dimension: str = "valid_time",
        area_dimension: str = "id",
        trim_period: bool = True,
    ):
        """
        Initialize the table for temporal localisation

        Args:
            da: xr.DataArray
                The DataArray to be localised.
            time_dimension: str = "valid_time"
                The name of the time dimension in the DataArray.
            area_dimension: str = "id"
                The name of the area dimension in the DataArray.
            trim_period: bool = True
                Whether to trim the DataArray to the period of interest.
        """
        self.table = da
        self.time_dimension = time_dimension
        self.area_dimension = area_dimension
        self.trim_period = trim_period

        tmp = self.table.sum(self.area_dimension)
        start_p = (
            tmp.where(tmp > 0)
            .dropna(self.time_dimension)[self.time_dimension][0]
            .values
        )
        end_p = (
            tmp.where(tmp > 0)
            .dropna(self.time_dimension)[self.time_dimension][-1]
            .values
        )

        self.table_shorten = self.table.sel(
            {self.time_dimension: slice(start_p, end_p)}
        )

    def update(self, trim_period: bool = True):
        """
        Update the DataArray.

        Args:
            trim_period: bool = True
                Whether to trim the DataArray to the period of interest.
        """
        self.trim_period = trim_period

    def new_division(self, delta_h: int = 3) -> xr.DataArray:
        """
        Create a new DataArray with a finer temporal resolution.

        Args:
            delta_h: int = 3
                The desired temporal resolution in hours.

        Returns:
            xr.DataArray
            The new DataArray with the finer temporal resolution.
        """
        if self.trim_period:
            table = self.table_shorten
        else:
            table = self.table

        # On va avoir différents cas en fonction de la taille
        # Si la taille est petite, on aura qu'un seul tableau
        # Si la taille est plus importante sans excéder les 9h
        #   on pourra avoir deux colonnes
        # Si la taille est encore plus grande, on aura 3 colonnes
        min_time = table[self.time_dimension].min()
        max_time = table[self.time_dimension].max()
        delta = max_time - min_time
        nb_hour = int(delta / np.timedelta64(1, "h")) + 1

        bounds: Optional[Union[Tuple[int], Tuple[int, int]]] = None
        if nb_hour >= 3 * delta_h:
            # Si le nombre d'heure est supérieur à 9 on peut avoir trois colonnes
            bounds = self.three_bounds(delta_h=delta_h)
        elif nb_hour >= 2 * delta_h:
            bounds = self.two_bounds(delta_h=delta_h)

        summary = []
        if bounds is None:
            summary.append(self.get_period_summary(table))
        elif len(bounds) == 1:
            tab1_f = table.sel(
                {
                    self.time_dimension: slice(
                        min_time, min_time + np.timedelta64(bounds[0], "h")
                    )
                }
            )
            tab2_f = table.sel(
                {
                    self.time_dimension: slice(
                        min_time + np.timedelta64(bounds[0] + 1, "h"), max_time
                    )
                }
            )
            summary.append(self.get_period_summary(tab1_f))
            summary.append(self.get_period_summary(tab2_f))
        else:  # when len(bounds)=2
            tab1_f = table.sel(
                {
                    self.time_dimension: slice(
                        min_time, min_time + np.timedelta64(bounds[0], "h")
                    )
                }
            )
            tab2_f = table.sel(
                {
                    self.time_dimension: slice(
                        min_time + np.timedelta64(bounds[0] + 1, "h"),
                        min_time + np.timedelta64(bounds[1], "h"),
                    )
                }
            )
            tab3_f = table.sel(
                {
                    self.time_dimension: slice(
                        min_time + np.timedelta64(bounds[1] + 1, "h"), max_time
                    )
                }
            )
            summary.append(self.get_period_summary(tab1_f))
            summary.append(self.get_period_summary(tab2_f))
            summary.append(self.get_period_summary(tab3_f))

        dout = xr.merge(summary)
        return dout["elt"]

    def two_bounds(self, delta_h: int) -> Optional[Tuple[int]]:
        """
        Find the indices of the first and second time steps that are separated by
        `delta_h` hours. The methodology is very crude : we look at each possibility
        and take the best. However, due to de problem size it seems we can afford it.

        Args:
            delta_h: int
                The desired temporal resolution in hours.

        Returns:
            Optional[Tuple[int, int]]
            The indices of the first and second time steps, or `None` if no such
            time steps exist.
        """
        if self.trim_period:
            table = self.table_shorten.astype(int)
        else:
            table = self.table.astype(int)

        # Retourne la période la premiere échéance avec un delta de 3H
        # On va maintenant fonctionner non pas en indice mais en horaire.
        #
        min_time = table[self.time_dimension].min()
        max_time = table[self.time_dimension].max()
        nb_hour = int((max_time - min_time) / np.timedelta64(1, "h"))
        error_min = table.size
        selected_bounds = None
        # On va boucler sur les heures
        # Globalement on va tester de min_time + 2 à max_time -2 si on peut être
        # sur la tranche qui change.

        for x in range(delta_h - 1, nb_hour - (delta_h - 1)):
            tab1 = table.sel(
                {
                    self.time_dimension: slice(
                        min_time, min_time + np.timedelta64(x, "h")
                    )
                }
            )
            tab1max = tab1.max(self.time_dimension)
            tab2 = table.sel(
                {
                    self.time_dimension: slice(
                        min_time + np.timedelta64(x + 1, "h"), max_time
                    )
                }
            )
            tab2max = tab2.max(self.time_dimension)
            error = ((tab1 - tab1max) ** 2).sum() + ((tab2 - tab2max) ** 2).sum()
            if error < error_min:
                error_min = error
                selected_bounds = [x]
        return selected_bounds

    def three_bounds(self, delta_h: int) -> Optional[Tuple[int, int]]:
        """
        Find the indices of the first and third time steps that are separated by
        `delta_h` hours.

        Args:
            delta_h: int
                The desired temporal resolution in hours.

        Returns:
            Optional[Tuple[int, int]]
            The indices of the first and third time steps, or `None` if no such
            time steps exist.
        """
        if self.trim_period:
            table = self.table_shorten.astype(int)
        else:
            table = self.table.astype(int)

        # Retourne la période la premiere échéance avec un delta de 3H
        # On va maintenant fonctionner non pas en indice mais en horaire.
        #
        min_time = table[self.time_dimension].min()
        max_time = table[self.time_dimension].max()
        nb_hour = int((max_time - min_time) / np.timedelta64(1, "h"))
        error_min = table.size
        selected_bounds = None
        # On va boucler sur les heures
        # Globalement on va tester de min_time + 2 à max_time -2 si on peut être
        # sur la tranche qui change.

        for x in range(delta_h - 1, nb_hour - (2 * delta_h - 1)):
            for y in range(x + delta_h, nb_hour - delta_h + 1):

                tab1 = table.sel(
                    {
                        self.time_dimension: slice(
                            min_time, min_time + np.timedelta64(x, "h")
                        )
                    }
                )
                tab1max = tab1.max(self.time_dimension)
                tab2 = table.sel(
                    {
                        self.time_dimension: slice(
                            min_time + np.timedelta64(x + 1, "h"),
                            min_time + np.timedelta64(y, "h"),
                        )
                    }
                )
                tab2max = tab2.max(self.time_dimension)
                tab3 = table.sel(
                    {
                        self.time_dimension: slice(
                            min_time + np.timedelta64(y + 1, "h"), max_time
                        )
                    }
                )
                tab3max = tab3.max(self.time_dimension)
                error = (
                    ((tab1 - tab1max) ** 2).sum()
                    + ((tab2 - tab2max) ** 2).sum()
                    + ((tab3 - tab3max) ** 2).sum()
                )
                if error < error_min:
                    error_min = error
                    selected_bounds = [x, y]
        return selected_bounds

    def get_period_summary(self, table: xr.DataArray) -> xr.Dataset:
        """
        Summarize information for the period.
        Take the maximum over the period as the value
        Take the period bounds to rename the period

        Args:
            table: xr.DataArray
                The table of the period.

        Returns:
            xr.Dataset
            The summary of the period.
        """
        res = xr.Dataset()
        value = table.max(self.time_dimension).astype(float)
        period_objet = table[self.time_dimension]
        p_name = (
            period_objet[0].dt.strftime("%Y%m%dT%H").values
            + "_to_"
            + period_objet[-1].dt.strftime("%Y%m%dT%H").values
        )
        LOGGER.debug(f"period_name is {p_name}")
        res["elt"] = value
        res = res.expand_dims("period").assign_coords(period=[p_name])
        return res

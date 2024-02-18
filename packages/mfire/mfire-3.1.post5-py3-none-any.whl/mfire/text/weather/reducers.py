from collections import defaultdict
from typing import Dict, List, Optional, Tuple, cast

import numpy as np

import mfire.utils.mfxarray as xr
from mfire.composite import WeatherComposite
from mfire.localisation import AltitudeInterval
from mfire.localisation.area_algebra import compute_IoL
from mfire.settings import get_logger
from mfire.text.base import BaseReducer
from mfire.text.period_describer import PeriodDescriber
from mfire.utils.calc import (
    all_combinations_and_remaining,
    combinations_and_remaining,
    round_to_previous_multiple,
)
from mfire.utils.date import Datetime, Period, Periods
from mfire.utils.dict_utils import KeyBasedDefaultDict
from mfire.utils.string_utils import concatenate_string, decapitalize
from mfire.utils.unit_converter import from_w1_to_wwmf
from mfire.utils.wwmf_utils import (
    are_wwmf_precipitations,
    are_wwmf_visibilities,
    is_wwmf_severe,
    is_wwmf_snow,
    wwmf_families,
    wwmf_label,
    wwmf_subfamilies,
)

# Logging
LOGGER = get_logger(name="weather_reducer.mod", bind="weather_reducer")


class WeatherReducer(BaseReducer):
    """Reducer class for the weather module.

    The "compute" method here takes a "WeatherComposite" object as input, which
    contains exactly one "weather" field.
    """

    # Structure of computed data
    _ts_info: defaultdict = KeyBasedDefaultDict(
        lambda wwmf: {
            "temporality": Periods(),
        }
    )

    # Dictionary giving the minimum values to be considered not isolated
    # The keys are the corresponding WWMF codes
    required_DT: defaultdict = defaultdict(lambda: 0.05)
    required_DHmax: defaultdict = defaultdict(lambda: 0.05)

    _times: Optional[List[Datetime]] = None
    _idAxis: Optional[str] = None

    @property
    def request_time(self) -> Datetime:
        """Returns the request time of the production."""
        weather_compo = cast(WeatherComposite, self.composite)
        return weather_compo.production_datetime

    @property
    def first_time(self) -> Datetime:
        """Returns the first time of the production."""
        if len(self._times) == 1:
            LOGGER.warning("There is only one valid_time to compute weather text.")
            return self._times[0]
        return self._times[0] - (self._times[1] - self._times[0])

    def _pre_process(self):
        """Pre-processing step."""
        # Clean old values
        self._ts_info.clear()
        self._idAxis = None

        self._times = [Datetime(d) for d in self.data.valid_time.to_numpy()]

        # Convert if necessary
        if self.data["wwmf"].units == "w1":
            self.data["wwmf"] = from_w1_to_wwmf(self.data["wwmf"])

        # Replace current codes with nebulosity
        replacing_codes = {72: 71, 73: 70, 78: 77, 82: 81, 83: 80}
        for old, new in replacing_codes.items():
            self.data["wwmf"] = self.data["wwmf"].where(
                self.data["wwmf"] != old, other=new
            )

    def _process(self):
        """
        Process the reduction by retrieving sensitive TS codes and storing their
        valid_time information.
        """

        dt_visibility, dh_max_visibility = 0.0, 0.0
        dt_precipitation, dh_max_precipitation = 0.0, 0.0

        previous_time = self.first_time
        for time in self._times:
            data_for_fixed_time: xr.DataArray = self.data.wwmf.sel(
                valid_time=time.as_np_dt64
            )
            all_ts, counts = np.unique(data_for_fixed_time, return_counts=True)

            dh_visibility, dh_precipitation = 0.0, 0.0
            for ts, count in zip(all_ts, counts):

                # Mist is not considered in order to avoid over-representation of the
                # Alpha model
                if ts == 31:
                    continue

                ts_families = wwmf_families(ts)
                if not ts_families:  # Skip if it's not a TS
                    continue

                self._ts_info[ts]["temporality"].append(
                    Period(begin_time=previous_time, end_time=time)
                )

                # Store the DHMax to remove isolated phenomenon later
                dh = (count / data_for_fixed_time.count()).item()

                if are_wwmf_visibilities(ts):
                    dh_visibility += dh
                else:
                    dh_precipitation += dh

            dt_visibility += dh_visibility / len(self._times)
            dt_precipitation += dh_precipitation / len(self._times)
            dh_max_visibility = max(dh_max_visibility, dh_visibility)
            dh_max_precipitation = max(dh_max_precipitation, dh_precipitation)

            previous_time = time

        # Remove isolated phenomenon
        ts_to_exclude = []
        if (
            not any(is_wwmf_severe(ts) for ts in self._ts_info)
            and dt_precipitation < self.required_DT["precipitation"]
            and dh_max_precipitation < self.required_DHmax["precipitation"]
        ):
            ts_to_exclude += [ts for ts in self._ts_info if are_wwmf_precipitations(ts)]
        if (
            dt_visibility < self.required_DT["visibility"]
            and dh_max_visibility < self.required_DHmax["visibility"]
        ):
            ts_to_exclude += [ts for ts in self._ts_info if are_wwmf_visibilities(ts)]
        for ts in ts_to_exclude:
            del self._ts_info[ts]

        # Apply different rules
        self._process_temporalities()

    def _describe(self, *args) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Generate a dictionary of descriptions based on the list of TS codes.

        Args:
            *args: List of TS codes.

        Returns:
            Dict[str, Dict[str, Optional[str]]]: Dictionary of descriptions.
        """
        # Sort the TS codes based on the begin time of temporality
        tuples = sorted(args, key=lambda x: x[1]["temporality"].begin_time)

        result = {}
        period_describer = PeriodDescriber(self.request_time)

        i = 1
        for (ts, info) in tuples:
            label = wwmf_label(*ts)
            if info.get("is_severe"):
                result["TSsevere"] = {
                    "label": decapitalize(label),
                    "localisation": self._process_localisation(ts, info["temporality"]),
                }
            else:
                # Check if there are multiple temporalities or if the first temporality
                # doesn't cover the entire requested time range
                if (
                    len(info["temporality"]) > 1
                    or info["temporality"][0].begin_time > self.first_time
                    or info["temporality"][0].end_time < self._times[-1]
                ):
                    temporality = period_describer.describe(
                        info["temporality"], to_reduce=False
                    )
                else:
                    temporality = None

                result[f"TS{i}"] = {
                    "label": label if temporality is None else decapitalize(label),
                    "temporality": temporality.capitalize()
                    if temporality is not None
                    else None,
                    "localisation": self._process_localisation(ts, info["temporality"]),
                }
                i += 1

        return result

    def _concat_infos(self, *args, is_severe: bool = False) -> dict:
        """
        Concatenate information by summing the temporalities.

        Args:
            *args: List of TS codes.
            is_severe (bool): Flag indicating if it's a severe phenomenon.

        Returns:
            dict: Concatenated information.
        """
        period_describer = PeriodDescriber(self.request_time)

        # Combine all the temporalities of the TS codes
        all_temporalities = Periods()
        for ts in args:
            all_temporalities += self._ts_info[ts]["temporality"]

        result = {"temporality": period_describer.reduce(all_temporalities)}

        loc = self._ts_info[args[0]].get("localisation")
        if loc is not None:
            result["localisation"] = loc
        if is_severe:
            result["is_severe"] = True
        return result

    def _process_temporalities(self):
        """
        Process all temporalities to remove short phenomena and apply grouping rules.

        This method reduces the temporalities and removes short phenomena from the data.
        It helps generate sentences and apply grouping rules accordingly.
        """
        ts_to_remove = []

        # Calculate the number of temporalities to keep based on the time range
        nbr_temporalities_to_keep = 2 + (self._times[-1] - self._times[0]).days

        for ts, info in self._ts_info.items():
            # Reduce the temporality using PeriodDescriber
            info["temporality"] = PeriodDescriber(self.request_time).reduce(
                info["temporality"], n=nbr_temporalities_to_keep
            )

            # Remove temporalities with total hours less than 3
            if info["temporality"].total_hours < 3:
                ts_to_remove.append(ts)

        # Remove the temporalities marked for removal
        for ts in ts_to_remove:
            del self._ts_info[ts]

    def _process_localisation(self, wwmf: List[int], temp: Periods) -> str:
        wwmf = [ts for ts in wwmf if ts not in [30, 31, 32]]
        if not wwmf:
            return ""

        # If there are snow and other kind of precipitations, only the snow is localized
        any_snow = any(is_wwmf_snow(ts) for ts in wwmf)
        if any_snow and any(not is_wwmf_snow(ts) for ts in wwmf):
            wwmf = [ts for ts in wwmf if is_wwmf_snow(ts)]

        map = (
            self.data.wwmf.isin(wwmf)
            .sel(
                valid_time=slice(
                    temp.begin_time.without_tzinfo, temp.end_time.without_tzinfo
                )
            )
            .sum("valid_time")
            > 0
        )

        weather_compo = cast(WeatherComposite, self.composite)
        geos_data = weather_compo.geos_data(self.geo_id)
        geos_data_size = geos_data.sum().data

        # Determine the location based on map and altitude information
        if map.sum().data / geos_data_size >= 0.9:
            return "sur tout le domaine"

        ratio_iol = compute_IoL(weather_compo.geos_descriptive(self.geo_id), map)
        if ratio_iol is not None:
            return (
                concatenate_string(ratio_iol.areaName.values)
                if ratio_iol.sum().data / geos_data_size < 0.9
                else "sur tout le domaine"
            )

        if not any_snow:
            return ""

        min_altitude = round_to_previous_multiple(
            weather_compo.altitudes("wwmf").where(map).min(), 100
        )
        if min_altitude - weather_compo.altitudes("wwmf").where(geos_data).min() < 100:
            # Take into account the minimum altitude of an area for localisation #38200
            return "sur tout le domaine"

        return (
            AltitudeInterval((min_altitude, np.inf)).name() if min_altitude > 0 else ""
        )

    def _merge_same_ts_family(self, *args) -> List[Tuple[List[int], dict]]:
        """
        This function takes a list of TS of the same family as an argument, merges them,
        and returns a list of tuples (list of TS, info) for all descriptions.

        Args:
            *args: Variable-length list of TS.

        Returns:
            List[Tuple[List[int], dict]]: List of tuples containing the TS code and
            information for each merged description.
        """
        ts1, ts2 = args[0], args[1]
        info1, info2 = self._ts_info[ts1], self._ts_info[ts2]

        nbr_args = len(args)
        if nbr_args == 2:
            different_temp = False
            if any(is_wwmf_severe(wwmf) for wwmf in args):
                hours_intersection = info1["temporality"].hours_of_intersection(
                    info2["temporality"]
                )
                hours_union = info1["temporality"].hours_of_union(info2["temporality"])
                if hours_intersection / hours_union < 0.75:
                    different_temp = True
            elif not info1["temporality"].are_same_temporalities(info2["temporality"]):
                different_temp = True

            # If TS are considered to have different temporalities
            if different_temp:
                return [([ts1], info1), ([ts2], info2)]

            return [([ts1, ts2], self._concat_infos(ts1, ts2))]

        if nbr_args == 3:
            ts3 = args[2]

            # We try to gather two of them according to the same possible temporality
            # and TS
            all_combinations = [ts1, ts2, ts3]
            for [_ts1, _ts2], [_ts3] in combinations_and_remaining(all_combinations, 2):
                _temp1 = self._ts_info[_ts1]["temporality"]
                _temp2 = self._ts_info[_ts2]["temporality"]
                _temp3 = self._ts_info[_ts3]["temporality"]

                if (
                    _temp1.are_same_temporalities(_temp2)
                    and not _temp1.are_same_temporalities(_temp3)
                    and not _temp2.are_same_temporalities(_temp3)
                ):
                    return [
                        ([_ts1, _ts2], self._concat_infos(_ts1, _ts2)),
                        ([_ts3], self._ts_info[_ts3]),
                    ]

            # If we can't gather two of them with the same temporality and TS
            return [([ts1, ts2, ts3], self._concat_infos(ts1, ts2, ts3))]

    def _post_process(self) -> dict:
        """
        Post-processes the data to be treated by the template key selector.

        Returns:
            dict: Post-processed data.
        """
        nbr_ts = len(self._ts_info)
        if nbr_ts == 0:
            return {}
        if nbr_ts == 1:
            return self._post_process_1_ts()
        if nbr_ts == 2:
            return self._post_process_2_ts()
        if nbr_ts == 3:
            return self._post_process_3_ts()
        return self._post_process_more_than_3_ts()

    def _post_process_1_ts(self) -> dict:
        """
        Post-processes data when there is only one TS.

        Returns:
            dict: Post-processed data.
        """
        items_iter = iter(self._ts_info.items())
        ts1, info1 = next(items_iter)

        return self._describe(([ts1], info1))

    def _post_process_2_ts(self) -> dict:
        """
        Post-processes data when there are two TS.

        Returns:
            dict: Post-processed data.
        """
        items_iter = iter(self._ts_info.keys())
        ts1 = next(items_iter)
        ts2 = next(items_iter)

        # If families are different we don't merge even if temporalities are the same
        if are_wwmf_visibilities(ts1) ^ are_wwmf_visibilities(ts2):
            info1, info2 = [self._ts_info[ts] for ts in [ts1, ts2]]
            return self._describe(([ts1], info1), ([ts2], info2))

        descriptions = self._merge_same_ts_family(ts1, ts2)
        return self._describe(*descriptions)

    def _post_process_3_ts(self) -> dict:
        """
        Post-processes data when there are three TS.

        Returns:
            dict: Post-processed data.
        """
        items_iter = iter(self._ts_info.items())
        ts1, _ = next(items_iter)
        ts2, _ = next(items_iter)
        ts3, _ = next(items_iter)

        # Same family
        if are_wwmf_visibilities(ts1, ts2, ts3) or are_wwmf_precipitations(
            ts1, ts2, ts3
        ):
            descriptions = self._merge_same_ts_family(
                ts1, ts2, ts3
            )  # Merge TS1, TS2, and TS3 with the same family
            return self._describe(*descriptions)

        # Different families
        all_combinations = [ts1, ts2, ts3]
        for [_ts1, _ts2], [_ts3] in combinations_and_remaining(all_combinations, 2):
            if are_wwmf_visibilities(_ts1, _ts2) or are_wwmf_precipitations(_ts1, _ts2):
                return self._describe(
                    ([_ts1, _ts2], self._concat_infos(_ts1, _ts2)),
                    ([_ts3], self._ts_info[_ts3]),
                )

    def _post_process_more_than_3_ts(self) -> dict:
        description_args = []

        visibility_codes, precipitation_codes = [], []
        for wwmf in self._ts_info.keys():
            (visibility_codes, precipitation_codes)[
                int(are_wwmf_precipitations(wwmf))
            ].append(wwmf)

        nbr_visibility_codes = len(visibility_codes)
        if nbr_visibility_codes > 0:
            visibility_infos = (
                self._concat_infos(*(wwmf for wwmf in visibility_codes if wwmf != 31))
                if visibility_codes != [31]
                else self._ts_info[31]
            )

            if nbr_visibility_codes == 2 and 31 in visibility_codes:
                visibility_codes = [
                    visibility_codes[0]
                    if visibility_codes[0] != 31
                    else visibility_codes[1]
                ]
            description_args.append((visibility_codes, visibility_infos))

        nbr_precipitation_codes = len(precipitation_codes)
        if nbr_precipitation_codes > 0:

            subfamilies = wwmf_subfamilies(*precipitation_codes)
            nbr_A_grp = sum(int(subfam.is_A_group) for subfam in subfamilies)

            if nbr_precipitation_codes == 1:
                description_args.append(
                    ([precipitation_codes[0]], self._ts_info[precipitation_codes[0]])
                )
            elif nbr_precipitation_codes in [2, 3]:
                description_args += self._merge_same_ts_family(*precipitation_codes)
            # We don't treat severe phenomenon as distinct
            elif nbr_A_grp == len(subfamilies) or nbr_A_grp < 3:
                for (combined_ts_1, combined_ts_2) in all_combinations_and_remaining(
                    precipitation_codes, is_symmetric=True
                ):
                    combined_temp_1 = [
                        self._ts_info[ts]["temporality"] for ts in combined_ts_1
                    ]
                    combined_temp_2 = [
                        self._ts_info[ts]["temporality"] for ts in combined_ts_2
                    ]
                    if not combined_temp_1[0].are_same_temporalities(
                        *combined_temp_1[1:]
                    ) or not combined_temp_2[0].are_same_temporalities(
                        *combined_temp_2[1:]
                    ):
                        continue

                    union_temp_1 = sum(combined_temp_1, start=Periods())
                    union_temp_2 = sum(combined_temp_2, start=Periods())
                    if not union_temp_1.are_same_temporalities(union_temp_2):
                        description_args.append(
                            (
                                combined_ts_1,
                                self._concat_infos(*combined_ts_1),
                            )
                        )
                        description_args.append(
                            (
                                combined_ts_2,
                                self._concat_infos(*combined_ts_2),
                            )
                        )
                        break
                else:
                    description_args.append(
                        (precipitation_codes, self._concat_infos(*precipitation_codes))
                    )
            # We treat severe phenomenon as distinct
            else:
                grp_A, grp_B = [], []
                for ts in precipitation_codes:
                    if ts in [49, 59, 84, 85, 98, 99]:
                        grp_B.append(ts)
                    else:
                        grp_A.append(ts)

                description_args.append((grp_A, self._concat_infos(*grp_A)))
                description_args.append(
                    (grp_B, self._concat_infos(*grp_B, is_severe=True))
                )
        return self._describe(*description_args)

    def compute(self, geo_id: str, composite: WeatherComposite) -> dict:
        super().compute(geo_id=geo_id, composite=composite)
        self._pre_process()
        self._process()
        return self._post_process()

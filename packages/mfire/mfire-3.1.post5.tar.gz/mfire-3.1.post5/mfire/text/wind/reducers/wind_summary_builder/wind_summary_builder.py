from __future__ import annotations

import traceback
from collections import OrderedDict
from typing import Optional, Tuple

import numpy as np
import pandas as pd

import mfire.utils.mfxarray as xr
from mfire.composite import WeatherComposite
from mfire.settings import get_logger
from mfire.text.wind.base import add_extra_content_to_summary
from mfire.text.wind.exceptions import WindSynthesisError, WindSynthesisNotImplemented
from mfire.text.wind.reducers.base_param_summary_builder import BaseParamSummaryBuilder
from mfire.text.wind.reducers.utils import initialize_previous_time
from mfire.text.wind.reducers.wind_summary_builder.helpers import (
    MetaData,
    PandasWindSummary,
    WindCase,
    WindFingerprint,
    WindSummaryBuilderMixin,
    WindType,
)
from mfire.text.wind.reducers.wind_summary_builder.wind_force import WindForce
from mfire.text.wind.reducers.wind_summary_builder.helpers.utils import (
    coords_dict_from_xr_coords,
)
from mfire.utils.date import Datetime

from .case1 import Case1SummaryBuilder
from .case2 import Case2SummaryBuilder
from .case3 import Case3SummaryBuilder

# Logging
LOGGER = get_logger(name="wind_summary_builder.mod", bind="wind_summary_builder")


class WindSummaryBuilder(WindSummaryBuilderMixin, BaseParamSummaryBuilder):
    """WindSummaryBuilder class.

    This class is able to compute a summary from a Dataset which contains wind and
    direction data. This summary is a dictionary.
    """

    THRESHOLD_MINUS_NUM: np.float64 = np.float64(10)
    WIND_FORCE: str = "wind"
    WIND_DIRECTION: str = "direction"
    WF_PERCENTILE_NUM: int = 95
    WF_TYPE2_DETECTION_PERCENT: int = 5
    WF_TYPE3_DETECTION_PERCENT: int = 5
    WF_TYPE3_CONFIRMATION_PERCENT: int = 10
    WF_TYPE_SEPARATORS: list[float] = [15.0, 30.0]  # Specified values are [15., 30.]
    CACHED_EXCEPTIONS: tuple[Exception] = (
        pd.errors.EmptyDataError,
        ValueError,
        WindSynthesisError,
        WindSynthesisNotImplemented,
    )

    def __init__(self, compo: WeatherComposite, data_array: xr.DataArray):
        """Initialize a WindSummaryBuilder class.

        TODO: data_array seems to be in fact a xr.Dataset because it is the
         WeatherComposite.data attribute which is a xr.Dataset !
        """

        # Call SummaryBuilderMixin.__init__ and create the summary attribute
        super().__init__()

        # Get composite units
        self.units: dict[str, str] = self._get_units_of_param(compo)

        # Get wind force data: nan values will be replaced by 0.0
        self.data_wf: xr.DataArray = self._get_data_array(
            data_array,
            self.WIND_FORCE,
            units=self.units[self.WIND_FORCE],
            nan_replace=0.0,
        )

        # Get wind direction data: nan values will be kept, 0 representing sur North
        # direction
        self.data_wd: xr.DataArray = self._get_data_array(
            data_array,
            self.WIND_DIRECTION,
            units=self.units[self.WIND_DIRECTION],
            values_to_replace=[(0.0, np.nan)],
        )

        self.metadata: MetaData = self._initialize_metadata()

        # Initialize pandas summary
        self.pd_summary = PandasWindSummary(self.data_wf.valid_time)

        self._preprocess()

    def _get_units_of_param(self, compo: WeatherComposite) -> dict[str, str]:
        """Get the units of the param as a string."""

        return {
            param_name: self._get_composite_units(compo, param_name)
            for param_name in [self.WIND_FORCE, self.WIND_DIRECTION]
        }

    @property
    def wind_types(self) -> tuple:
        """Get the wind types of all terms as a tuple."""
        return self.pd_summary.wind_types

    @property
    def wind_types_set(self) -> set:
        """Get the wind types of all terms as a set."""
        return self.pd_summary.wind_types_set

    @property
    def fingerprint_raw(self) -> Optional[str]:
        """Get the raw fingerprint from the pandas summary."""
        return self.pd_summary.data.attrs.get("fingerprint_raw")

    @property
    def threshold(self) -> float:
        """Get the threshold from the metadata attribute."""
        return self.metadata.threshold

    def _initialize_metadata(self) -> MetaData:
        """ "Initialize the metadata attribute."""
        return MetaData(data_points_counter=self._count_data_points(self.data_wf))

    def count_points(self, term_data: xr.DataArray, condition) -> Tuple[int, float]:
        """Count the points of a term regarding a particular condition."""
        mask = term_data.where(condition)
        count: int = int(mask.count())
        percent: float = count * 100.0 / int(self.metadata.data_points_counter)
        return count, percent

    def _does_term_wind_force_data_match_input_conditions(
        self,
        term_wind_force_data: xr.DataArray,
        wind_force_bound: float,
        percent_min: float,
        metadata_attr: Optional[str] = None,
    ) -> bool:
        """Check if the input wind force data match input bound and percent.

        If metadata_attr is given, then the related attribute of MetaData is updated.
        """
        count: int
        percent: float

        # Get the percent of points with a wind force >= wind_force_bound km/h
        count, percent = self.count_points(
            term_wind_force_data, term_wind_force_data >= wind_force_bound
        )

        # Update percent_max in metadata if asked
        if metadata_attr:
            percent_max: float = max(getattr(self.metadata, metadata_attr), percent)
            setattr(self.metadata, metadata_attr, percent_max)

        # If percent >= percent_min, then return True, else False
        if percent >= percent_min:
            return True
        return False

    def _get_term_type(self, term_wind_force_data: xr.DataArray):
        """Get the type of the given term_data."""
        # Check if the current term is a type 3 ?
        if (
            self._does_term_wind_force_data_match_input_conditions(
                term_wind_force_data,
                self.WF_TYPE_SEPARATORS[1],
                self.WF_TYPE3_DETECTION_PERCENT,
                "t3_percent_max_detection",
            )
            is True
        ):
            return WindType.TYPE_3

        # Check if the current term is a type 2 ?
        if (
            self._does_term_wind_force_data_match_input_conditions(
                term_wind_force_data,
                self.WF_TYPE_SEPARATORS[0],
                self.WF_TYPE2_DETECTION_PERCENT,
                "t2_percent_max_detection",
            )
            is True
        ):
            return WindType.TYPE_2

        return WindType.TYPE_1

    def _preprocess(self):
        """Type terms and get the thresholds."""
        accumulated_data: np.ndarray = np.array([])
        wfq_max: np.float64 = np.float64(0.0)
        valid_times: np.ndarray = self.data_wf.valid_time.values

        # Initialize previous_time
        previous_time: np.datetime64 = initialize_previous_time(valid_times)

        for valid_time in valid_times:
            term_data_wf: xr.DataArray = self.data_wf.sel(valid_time=valid_time)

            # Type the term data
            self.pd_summary.data.loc[
                valid_time, self.pd_summary.COL_WT
            ] = self._get_term_type(term_data_wf)

            # Set the previous_time 0of the current term
            self.pd_summary.data.loc[
                valid_time, self.pd_summary.COL_PREVIOUS_TIME
            ] = previous_time

            # Accumulate data
            accumulated_data = np.concatenate(
                (accumulated_data, term_data_wf.values), axis=None
            )

            # Compute the maximum of the terms Q95
            wfq: float = WindForce.data_array_to_value(
                self.data_wf.sel(valid_time=valid_time)
            )
            wfq_max = np.maximum(wfq, wfq_max)

            previous_time = valid_time

        # Set the threshold
        wfq_max = wfq_max - self.THRESHOLD_MINUS_NUM
        q_accumulated = (
            np.percentile(accumulated_data, self.WF_PERCENTILE_NUM)
            - self.THRESHOLD_MINUS_NUM
        )
        self.metadata.threshold_accumulated = round(max(float(q_accumulated), 0), 1)
        self.metadata.threshold_hours_max = round(max(float(wfq_max), 0), 1)
        self.metadata.threshold = self.metadata.threshold_accumulated

        # Round percent_max_detection
        self.metadata.t3_percent_max_detection = round(
            self.metadata.t3_percent_max_detection, 1
        )
        self.metadata.t2_percent_max_detection = round(
            self.metadata.t2_percent_max_detection, 1
        )

        # Filter type 3 terms
        if WindType.TYPE_3 in self.wind_types:
            self._filter_wind_type3_terms(self.threshold)

        LOGGER.debug(f"terms types: {self.wind_types_set}")

        # Add raw WindFingerprint in pandas attributes
        self.pd_summary.add_attr("fingerprint_raw", WindFingerprint(self.wind_types))

        # Filter wind force and wind direction data
        self._filter_wind_data(self.case_family)

    def _filter_wind_type3_terms(self, lower_bound: float) -> int:
        """Set type 3 terms with not enough high wind points to type 2."""
        type3_terms_cnt: int = 0

        for valid_time in self.pd_summary.index:
            if self.pd_summary.get_term_wind_type(valid_time) != WindType.TYPE_3:
                continue

            # Compute percent of points where the wind speed is >= lower_bound
            data_wf: xr.DataArray = self.data_wf.sel(valid_time=valid_time)
            _, percent = self.count_points(data_wf, data_wf >= lower_bound)

            # update t3_percent_max_confirmation
            self.metadata.t3_percent_max_confirmation = max(
                self.metadata.t3_percent_max_confirmation, percent
            )

            if percent < self.WF_TYPE3_CONFIRMATION_PERCENT:
                self.pd_summary.data.loc[
                    valid_time, self.pd_summary.COL_WT
                ] = WindType.TYPE_2
            else:
                type3_terms_cnt += 1

        if type3_terms_cnt == 0:
            LOGGER.debug("All type 3 terms have been filtered")

        # Round t3_percent_max_confirmation
        self.metadata.t3_percent_max_confirmation = round(
            self.metadata.t3_percent_max_confirmation, 1
        )

        return type3_terms_cnt

    def _set_filtering_thresholds(self, case: WindCase):
        """Set thresholds which will be used during the data filtering step."""
        if case == WindCase.CASE_3:
            self.metadata.filtering_threshold_t3 = self.threshold
            self.metadata.filtering_threshold_t2 = self.WF_TYPE_SEPARATORS[0]
        elif case == WindCase.CASE_2:
            self.metadata.filtering_threshold_t2 = max(
                self.threshold, self.WF_TYPE_SEPARATORS[0]
            )
        else:
            pass

    def _filter_wind_data(self, case_family: WindCase) -> None:
        """Filter wind data.

        It keeps only type 2 and type 3 terms. And for all kept terms, we keep only
        direction data when wind force >= threshold.
        """
        array_wf: Optional[np.ndarray] = None
        array_wd: Optional[np.ndarray] = None
        valid_times: list[np.ndarray] = []

        if case_family == WindCase.CASE_1:
            return

        if case_family not in [WindCase.CASE_2, WindCase.CASE_3]:
            raise ValueError(f"Bad case_family: '{case_family}' !")

        self._set_filtering_thresholds(case_family)

        for valid_time in self.data_wf["valid_time"].values:
            # Get Wind type od current term
            wind_type_value: int = self.pd_summary.get_term_wind_type(valid_time)
            wind_type: WindType = WindType(wind_type_value)

            # If Wind type 1, then do not keep related wf and wd
            if wind_type == WindType.TYPE_1:
                continue

            # Check wind force data of the current term and do not keep it if all
            # values are <= lower_bound
            values_wf: np.ndarray = self.data_wf.sel(valid_time=valid_time).values

            filtering_threshold: float
            if wind_type == WindType.TYPE_2:
                filtering_threshold = self.metadata.filtering_threshold_t2
            else:
                filtering_threshold = self.metadata.filtering_threshold_t3

            mask = np.where(values_wf >= filtering_threshold, True, False)
            if mask.all() is False:
                continue

            # Get wind direction data
            values_wd: np.ndarray = self.data_wd.sel(valid_time=valid_time).values
            valid_times.append(valid_time)

            # Concatenate data in numpy arrays array_wf and array_wd:
            # wind direction data are filtered but not wind force data
            if array_wf is None:  # 1st iteration
                array_wf = np.array([np.where(mask, values_wf, np.nan)])
                array_wd = np.array([np.where(mask, values_wd, np.nan)])
            else:
                array_wf_new: np.ndarray = np.where(mask, values_wf, np.nan)
                array_wf = np.concatenate(
                    (array_wf, array_wf_new[np.newaxis, :, :]), axis=0
                )

                array_wd_new: np.ndarray = np.where(mask, values_wd, np.nan)
                array_wd = np.concatenate(
                    (array_wd, array_wd_new[np.newaxis, :, :]), axis=0
                )

        # Set coordinates
        coords: dict = coords_dict_from_xr_coords(
            self.data_wf.coords,
            {"valid_time": pd.Series(valid_times)},
            exclude=["areaName", "areaType"],
        )

        # Generate filtered wind force data
        data_wf = xr.DataArray(
            array_wf, coords=coords, dims=self.data_wf.dims, attrs=self.data_wf.attrs
        )
        self.data_wf = data_wf

        # Generate filtered wind direction data
        data_wd = xr.DataArray(
            array_wd, coords=coords, dims=self.data_wd.dims, attrs=self.data_wd.attrs
        )
        self.data_wd = data_wd

    @property
    def case_family(self) -> WindCase:
        """WindCase family depending on term types."""
        wind_types_set: set = self.wind_types_set

        if not wind_types_set or wind_types_set == {WindType.TYPE_1}:
            return WindCase.CASE_1

        if WindType.TYPE_3 not in self.wind_types:
            return WindCase.CASE_2

        return WindCase.CASE_3

    def _export_metadata_with_extra_info(self, case: WindCase) -> str:
        """Export Metadata content and extra info like case nbr as string.

        Elements as ordered as following:
        case, threshold_accumulated, threshold_hours_max, threshold,
        t3_percent_max_detection, t3_percent_max_confirmation
        """

        LOGGER.debug(f"metadata: {self.metadata}")

        output = OrderedDict(
            {"case": str(case.value[-1]), "metadata": self.metadata.to_string()}
        )

        return ", ".join(list(output.values()))

    def compute(self, reference_datetime: Datetime) -> dict:
        """Compute the summary and set the ERROR case if something went wrong.

        This method catch pd.errors.EmptyDataError and ValueError exception and:
        - set case nbr as ERROR in the summary
        - add a message with the exception in the summary
        """
        try:
            self._generate_summary(reference_datetime)
        except self.CACHED_EXCEPTIONS as exp:
            msg: str = (
                f"{exp.__class__.__name__}: problem detected in WindSummaryBuilder -> "
                f"{exp}\nFingerprint: '{self.fingerprint_raw}'\n"
                f"{traceback.format_exc()}"
            )

            self._add_error_case_in_summary(self._summary, msg)

        self.pd_summary.add_attr(self.SELECTOR_KEY, self.case_value)

        return {self.WIND_FORCE: self._summary}

    def _generate_summary(self, reference_datetime: Datetime) -> None:
        """Generate the summary."""
        case_family: WindCase = self.case_family

        # Case 1: there is only data_arrays with type 1
        if case_family == WindCase.CASE_1:
            self._summary = Case1SummaryBuilder().run()

        else:
            # Initialize summary
            self._summary = {"units": self.units[self.WIND_FORCE]}
            sub_summary: dict

            # Case 2: there is only data_arrays with type 1 and type 2
            if case_family == WindCase.CASE_2:
                summary_builder: Case2SummaryBuilder = Case2SummaryBuilder()
                sub_summary = summary_builder.run(
                    self.pd_summary,
                    reference_datetime,
                    self.data_wd,
                )

            # Case 3: there is data_arrays with type 3
            elif case_family == WindCase.CASE_3:
                summary_builder: Case3SummaryBuilder = Case3SummaryBuilder(
                    self.pd_summary, self.data_wd, self.data_wf
                )
                sub_summary = summary_builder.run(reference_datetime)

            else:
                raise ValueError(f"Bad case_family '{case_family}' !")

            self._summary.update(sub_summary)

        # Add extra content: usefull for understand output
        add_extra_content_to_summary(
            self._summary, self._export_metadata_with_extra_info(case=case_family)
        )

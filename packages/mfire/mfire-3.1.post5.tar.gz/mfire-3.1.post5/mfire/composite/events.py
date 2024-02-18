from __future__ import annotations

import copy
import operator
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import numpy as np
from pydantic import BaseModel
from pydantic import Field as PydanticField
from pydantic import StrictInt, root_validator, validator

import mfire.utils.mfxarray as xr
from mfire.composite.aggregations import Aggregation, AggregationMethod, Aggregator
from mfire.composite.base import BaseComposite
from mfire.composite.fields import FieldComposite
from mfire.composite.geos import AltitudeComposite, GeoComposite
from mfire.composite.operators import ComparisonOperator
from mfire.settings import get_logger
from mfire.utils.calc import all_close
from mfire.utils.string_utils import split_accumulation_var_name
from mfire.utils.unit_converter import get_unit_context, unit_conversion
from mfire.utils.xr_utils import ArrayLoader, Loader, da_set_up, sum_with_nan

# Logging
LOGGER = get_logger(name="composite.events.mod", bind="composite.events")


class Category(str, Enum):
    """Création d'une classe d'énumération contenant les categories possibles
    des unités
    """

    BOOLEAN = "boolean"
    QUANTITATIVE = "quantitative"
    CATEGORICAL = "categorical"
    RESTRICTED_QUANTITATIVE = "restrictedQuantitative"


class Threshold(BaseModel):
    """Create a Threshold object containing the configuration of the plain and mountain
        objects for the Promethee production task.

    Args:
        baseModel: Model from the pydantic library.

    Returns:
        baseModel: Threshold object.
    """

    threshold: Union[float, str, bool, List[Union[float, str]]]
    comparison_op: ComparisonOperator
    units: Optional[Union[StrictInt, str]]
    next_critical: Optional[float] = None

    def __eq__(self, other: Threshold):
        return all(
            (
                self.comparison_op == other.comparison_op,
                self.units == other.units,
                all_close(self.next_critical, other.next_critical),
                all_close(self.threshold, other.threshold),
            )
        )

    @validator("threshold")
    def validate_threshold(cls, value):
        """
        Validator to validate the threshold value.

        Args:
            value: The threshold value to be validated.

        Returns:
            Any: The validated threshold value.
        """

        if isinstance(value, list):
            return list(
                map(
                    lambda x: int(x) if isinstance(x, float) and int(x) == x else x,
                    value,
                )
            )

        return int(value) if isinstance(value, float) and int(value) == value else value

    @root_validator(pre=True)
    def check_comparison_op_and_value(cls, values: dict) -> dict:
        """
        Validates the comparison operator and threshold.

        Args:
            values (dict): The input values.

        Returns:
            dict: The validated values.
        """
        if (
            isinstance(values["threshold"], List)
            and values["comparison_op"] == ComparisonOperator.EGAL
        ):
            if len(values["threshold"]) > 1:
                values["comparison_op"] = ComparisonOperator.ISIN
            else:
                values["threshold"] = values["threshold"][0]
        return values

    def change_units(self, new_units: str, context: Optional[str] = None) -> Threshold:
        """This function changes the threshold to match the units of the field.

        Args:
            new_units (str): New units to convert.
            context (Optional[str]): Possible context for DataArray.

        Returns:
            Threshold: The modified threshold.
        """
        threshold = copy.deepcopy(self)
        if isinstance(threshold.units, str) and threshold.units != new_units:
            threshold.threshold = unit_conversion(
                (threshold.threshold, threshold.units), new_units, context=context
            )
            if threshold.next_critical is not None:
                threshold.next_critical = unit_conversion(
                    (threshold.next_critical, threshold.units),
                    new_units,
                    context=context,
                )
            threshold.units = new_units
        return threshold

    def update_next_critical(
        self,
        threshold: Threshold,
    ):
        """
        This function updates the next_critical value of threshold. It adds an
        information (next_critical) about the threshold of the next higher level.
        If a next_critical value exists, it checks if the value of that level is
        less critical.

        Args:
            threshold (Threshold): The dictionary of another threshold
        """

        if (
            self.comparison_op.is_order
            and self.comparison_op == threshold.comparison_op
        ):
            # In this case, we will check if the value is more critical
            # than the base value and less critical than the next one
            # Check if the value is more critical than the current one
            threshold = threshold.change_units(self.units)
            if self.comparison_op(threshold.threshold, self.threshold):
                if self.next_critical is not None:
                    # If there is already a next_critical value.
                    # If the new critical value is less critical.
                    if self.comparison_op(threshold.threshold, self.next_critical):
                        self.next_critical = threshold.threshold
                else:
                    self.next_critical = threshold.threshold


class EventComposite(BaseComposite):
    """Create an Element object containing the configuration of the event elements
    for the Promethee production task.

    Args:
        baseModel (Model): Model from the pydantic library.

    Returns:
        baseModel (Element): Element object.
    """

    class Config:
        copy_on_model_validation = False

    field: FieldComposite
    category: Category
    plain: Optional[Threshold]
    mountain: Optional[Threshold]
    mountain_altitude: Optional[int]
    altitude: AltitudeComposite
    process: Optional[str]
    geos: Union[GeoComposite, xr.DataArray]
    time_dimension: Optional[str]
    aggregation: Optional[Aggregation]
    aggregation_aval: Optional[Aggregation]
    compute_list: Optional[List[str]] = []

    _mask: Optional[xr.MaskAccessor] = None
    _values_ds: xr.Dataset = xr.Dataset()
    _field_da: Optional[xr.DataArray] = None

    @validator("mountain", always=True)
    def check_plain_or_mountain(cls, val: Optional[Threshold], values):
        if not values.get("plain") and not val:
            raise ValueError("Either plain or mountain is required")
        return val

    @validator("compute_list")
    def check_compute_list(cls, val: Optional[List[str]] = None) -> List[str]:
        """Validate the compute_list field and ensure it's a list.

        Args:
            v (Optional[List[str]]): List of compute strings.

        Returns:
            List[str]: Validated and formatted compute list.
        """
        if val is None:
            return []
        return val

    @property
    def compute_aggregated_values(self):
        return (
            self.aggregation is not None
            and not self.aggregation.method.is_after_threshold
        )

    @property
    def values_ds(self) -> Optional[xr.Dataset]:
        """Get the values dataset.

        Returns:
            Optional[xr.Dataset]: Values dataset.
        """
        return self._values_ds

    @property
    def geos_da(self):
        return self.geos.compute() if isinstance(self.geos, GeoComposite) else self.geos

    @property
    def mask(self) -> Optional[xr.MaskAccessor]:
        """Get the mask.

        Returns:
            Optional[xr.MaskAccessor]: Mask accessor.
        """
        if self._mask is None:
            geos_mask_da = da_set_up(self.geos_da, self.field_da).mask.f32

            alt_field_da = self.altitude.compute()
            alt_mask_da = da_set_up(alt_field_da, self.field_da).notnull()
            self._mask = (geos_mask_da * alt_mask_da).mask
        return self._mask

    @property
    def field_da(self) -> Optional[xr.DataArray]:
        """Get the values dataset.

        Returns:
            Optional[xr.DataArray]: Values dataset.
        """
        if self._field_da is None:
            self._field_da = self.field.compute()
        return self._field_da

    @property
    def _cached_attrs(self) -> dict:
        """Get the cached attribute dictionary.

        Returns:
            dict: Dictionary containing the cached attributes and their corresponding
                loaders.
        """
        return {
            "data": ArrayLoader,  # Cached attribute for data with ArrayLoader
            "values_ds": Loader,  # Cached attribute for values_ds with Loader
        }

    def _compute(self, **_kwargs) -> Optional[Union[xr.DataArray, xr.Dataset]]:
        """
        Compute the event based on the initialized fields and return the data as a
        DataArray.

        Returns:
            xr.DataArray: The computed data of the event.
        """
        # Compute for plain and mountain
        risk_da = self.compute_plain_and_mountain()

        # Aggregate if necessary
        return self.compute_downstream_aggregation(risk_da=risk_da)

    def get_comparison(self) -> dict:
        """
        Get the comparison operator for an event.

        Returns:
            dict: Dictionary of comparison operator (on plain or mountain). Here
                is an example of the results:
                {
                    "plain": Threshold(...),
                    "mountain": Threshold(...),
                    "category": ...,
                    "mountain_altitude": ...,
                    "aggregation": ...,
                }
        """
        dict_out: Dict[str, Any] = {"category": self.category}
        if self.plain is not None:
            dict_out["plain"] = self.plain
        if self.mountain is not None:
            dict_out["mountain"] = self.mountain
        if self.mountain_altitude is not None:
            dict_out["mountain_altitude"] = self.mountain_altitude

        # Get the aggregation function. Will be used for future checks.
        aggregation_func = (
            self.aggregation if self.aggregation is not None else self.aggregation_aval
        )
        dict_out["aggregation"] = dict(aggregation_func or {})
        return dict_out

    @property
    def cover_period(self) -> Optional[xr.DataArray]:
        """Return the period cover by the event. To do so, we will need to open the
        DataArray

        Returns:
            xr.DataArray: Period covering the event.
        """
        return (
            copy.deepcopy(self.field.get_coord(self.time_dimension))
            if self.time_dimension is not None
            else None
        )

    def update_selection(
        self,
        new_sel: dict,
        new_slice: dict,
        new_isel: dict,
        new_islice: dict,
    ):
        """
        Update the selection of the field and field_1.

        Args:
            new_sel (dict): Selection dictionary for the field.
            new_slice (dict): Slice dictionary for the field.
            new_isel (dict): Index selection dictionary for the field.
            new_islice (dict): Index slice dictionary for the field.
        """
        # Update selection for the main field
        if (selection := self.field.selection) is not None:
            selection.update(
                new_sel=new_sel,
                new_slice=new_slice,
                new_isel=new_isel,
                new_islice=new_islice,
            )

        # Update selection for field_1 if it exists
        if (field_1 := getattr(self, "field_1", None)) is not None:
            if (selection := field_1.selection) is not None:
                selection.update(
                    new_sel=new_sel,
                    new_slice=new_slice,
                    new_isel=new_isel,
                    new_islice=new_islice,
                )

    def get_risk(
        self,
        field_da: xr.DataArray,
        threshold: Threshold,
    ) -> xr.DataArray:
        """Function created to allow other child classes to implement the risk in
            another way.

        Args:
            field_da (xr.DataArray): The field.
            threshold (Any): The threshold applied.
            mask_da (xr.DataArray): The mask.

        Returns:
            xr.DataArray: The risk for every pixel. Be careful: The returned result
            is in format f32
        """
        result = threshold.comparison_op(field_da, threshold.threshold)
        return xr.where(field_da.notnull(), result, np.nan)

    def compute_density(self, risk_field_da: xr.DataArray) -> xr.DataArray:
        """Compute the density of an event.

        This function calculates the density of an event, regardless of the
        aggregation method used (e.g., average, DRR).

        Args:
            risk_field_da (xr.DataArray): Risk field

        Returns:
            xr.DataArray: Risk density
        """
        agg_handler = Aggregator(risk_field_da)
        density = agg_handler.compute(Aggregation(method=AggregationMethod.DENSITY))
        return density

    def compute_summarized_density(
        self, risk_field_da: xr.DataArray, mask_da: xr.DataArray
    ) -> xr.DataArray:
        """Compute the summarized density over time.

        Args:
            risk_field_da (xr.DataArray): Risk field.
            mask_da (xr.DataArray): Mask.

        Returns:
            xr.DataArray: Summarized density over time.
        """
        # Aggregate the risk field over time using the maximum threshold
        agg_handler_time = Aggregator(risk_field_da, aggregate_dim=self.time_dimension)
        max_risk = (
            agg_handler_time.compute(Aggregation(method=AggregationMethod.MAX))
            * mask_da
        )

        # Compute the density using the maximum risk field
        agg_handler_space = Aggregator(max_risk)
        density = agg_handler_space.compute(
            Aggregation(method=AggregationMethod.DENSITY)
        )
        return density

    def get_extreme_values(
        self, field_da: xr.DataArray, original_unit: str
    ) -> Tuple[Optional[xr.DataArray], Optional[xr.DataArray]]:
        """
        Get extreme values: Returns the minimum and maximum values.

        Arguments:
            field_da (xr.DataArray) -- The DataArray for which to find the
                minimum and maximum.
            original_unit (str) -- The original unit of the data.

        Returns:
            Tuple[Optional[xr.DataArray], Optional[xr.DataArray]] -- The two DataArrays
                representing the minimum and maximum values.
        """
        if self.category not in (
            Category.QUANTITATIVE,
            Category.RESTRICTED_QUANTITATIVE,
        ):
            return None, None

        agg_handler = Aggregator(field_da)
        min_agg = Aggregation(method=AggregationMethod.MIN)
        max_agg = Aggregation(method=AggregationMethod.MAX)
        min_da = unit_conversion(agg_handler.compute(min_agg), original_unit)
        max_da = unit_conversion(agg_handler.compute(max_agg), original_unit)
        return min_da, max_da

    def get_representative_values(
        self,
        field_da: xr.DataArray,
        threshold: Threshold,
    ) -> Optional[xr.DataArray]:
        """
        Returns the representative threshold of the field. Handles aggregation by mean
        and density ratio regions (if the comparison operator is in [<,<=,>,>=]).

        Args:
            field_da (xr.DataArray): The field.
            threshold (Threshold): the threshold of the current event

        Returns:
            Optional[xr.DataArray]: The representative threshold. Returns None if the
                variable is qualitative/boolean or an error occurred.

        Raises:
            ValueError: If the comparison operator is not in [<,<=,>,>=, inf, infegal,
                sup, supegal] and the aggregation method is density ratio regions.
        """
        # Check if the category is quantitative or restricted quantitative
        if self.category not in (
            Category.QUANTITATIVE,
            Category.RESTRICTED_QUANTITATIVE,
        ):
            return None

        agg_handler = Aggregator(field_da)
        prefix, _, _ = split_accumulation_var_name(str(field_da.name))

        # Determine the aggregation method
        aggregation = (
            self.aggregation
            or self.aggregation_aval
            or Aggregation(method=AggregationMethod.MEAN)
        )
        LOGGER.debug(
            "Aggregation method",
            aggregation=aggregation,
            place="event",
            func="get_representative_values",
        )

        # Perform aggregation based on the method
        if not aggregation.method.is_after_threshold:
            # Aggregation by mean or other non-threshold methods
            rep_value = agg_handler.compute(aggregation)
        elif aggregation.method.startswith("requiredDensity"):
            if prefix in ["PRECIP", "EAU"]:
                thresh = 0.75
            elif prefix == "NEIPOT":
                thresh = 0.5
            else:
                thresh = 0.9
            try:
                if threshold.comparison_op.is_increasing_order:
                    quantile = thresh
                elif threshold.comparison_op.is_decreasing_order:
                    quantile = 1 - thresh
                else:
                    LOGGER.error(
                        f"Unknown case {threshold.comparison_op}",
                        func="get_representative_values",
                    )
                    raise ValueError(
                        f"Representative value is not possible to give with comparison "
                        f"operator {threshold.comparison_op}"
                    )  # Compute the desired quantile

                rep_value = agg_handler.compute(
                    Aggregation(
                        method=AggregationMethod.QUANTILE, kwargs={"q": quantile}
                    )
                ).drop_vars("quantile")

            except Exception as excpt:
                # Handle aggregation failure
                LOGGER.error(
                    f"Aggregation failed on the field: {field_da}",
                    comparison_op=threshold.comparison_op,
                    field=field_da,
                    func="get_representative_values",
                    excpt=excpt,
                )
                raise ValueError from excpt
        else:
            # Invalid aggregation method
            LOGGER.error(
                f"Unknown aggregation method: {aggregation.method}",
                func="get_representative_values",
            )
            raise ValueError(
                f"Representative value is not possible to give with aggregation "
                f"method: {aggregation.method}"
            )

        # Convert to the original unit
        rep_value = unit_conversion(rep_value, threshold.units)
        return rep_value

    def _compute_values(self, field: xr.DataArray, kind: Literal["plain", "mountain"]):
        threshold = self.plain if kind == "plain" else self.mountain

        if self.category in (
            Category.QUANTITATIVE,
            Category.RESTRICTED_QUANTITATIVE,
        ):
            self._values_ds[f"threshold_{kind}"] = threshold.threshold

        if "extrema" in self.compute_list:
            (mini, maxi) = self.get_extreme_values(field, threshold.units)
            if mini is not None:
                self._values_ds[f"min_{kind}"] = mini
                self._values_ds[f"max_{kind}"] = maxi

        if "representative" in self.compute_list:
            rep_value = self.get_representative_values(field, threshold=threshold)
            if rep_value is not None:
                self._values_ds[f"rep_value_{kind}"] = rep_value

    def compute_plain_and_mountain(self) -> xr.DataArray:
        """
        Compute the risk and various representative/extreme values for plain or plain
        and mountain.

        Returns:
            xr.DataArray: Risk for plain and mountain.
        """
        risk_field = None
        plain_field, plain_threshold = None, None
        mountain_field, mountain_threshold = None, None

        alt_field_da = self.altitude.compute()
        unit_context = get_unit_context(str(self.field_da.name))

        if self.plain is not None:
            plain_threshold = self.plain.change_units(
                self.field_da.units, context=unit_context
            )
            if self.mountain_altitude is not None:
                plain_mask = (alt_field_da <= self.mountain_altitude) * self.mask.bool
                plain_mask = plain_mask.mask.f32
            else:
                plain_mask = self.mask.f32

            plain_field = self.field_da * plain_mask
            plain_field.name = self.field_da.name

            risk_field = self.get_risk(plain_field, plain_threshold)

            self._compute_values(plain_field, "plain")

        if self.mountain is not None:
            mountain_threshold = self.mountain.change_units(
                self.field_da.units, context=unit_context
            )
            mountain_mask = (alt_field_da > self.mountain_altitude) * self.mask.bool
            mountain_mask = mountain_mask.mask.f32
            mountain_field = self.field_da * mountain_mask
            mountain_field.name = self.field_da.name

            mountain_risk = self.get_risk(mountain_field, mountain_threshold)
            risk_field = (
                sum_with_nan(risk_field, mountain_risk)
                if risk_field is not None
                else mountain_risk
            )

            self._compute_values(mountain_field, "mountain")

        if "density" in self.compute_list:
            self._values_ds["density"] = self.compute_density(risk_field)

        if "summary" in self.compute_list:
            self._values_ds["summarized_density"] = self.compute_summarized_density(
                risk_field, self.mask.bool
            )

        if self.compute_aggregated_values:
            risk_field = None

            if self.plain is not None:
                plain_field = Aggregator(plain_field).compute(self.aggregation)
                risk_field = self.get_risk(plain_field, plain_threshold)

            if self.mountain is not None:
                mountain_field = Aggregator(mountain_field).compute(self.aggregation)
                mountain_risk = self.get_risk(mountain_field, mountain_threshold)
                risk_field = (
                    sum_with_nan(risk_field, mountain_risk)
                    if risk_field is not None
                    else mountain_risk
                )

        risk_field.name = self.field_da.name
        return risk_field

    def compute_downstream_aggregation(self, risk_da: xr.DataArray) -> xr.DataArray:
        """
        Calculate the risk. If aggregation is specified, it can be done before (
            mean/quantile/...) or after the comparison with the operator (ddr/density).
            This function can take into account altitude conditions (if they have been
            properly specified).

        Args:
            risk_da (xr.DataArray): The risk DataArray.

        Returns:
            xr.DataArray: The risk DataArray for this "unit" event.
        """
        new_risk_da = risk_da

        # Perform aggregation if specified and the method is after the threshold
        if self.aggregation is not None and self.aggregation.method.is_after_threshold:
            agg_handler = Aggregator(new_risk_da)
            new_risk_da = agg_handler.compute(self.aggregation)

        # Perform the occurrence of event
        occurrence_event = new_risk_da > 0
        occurrence_event.attrs = {}
        if self.aggregation is None:
            occurrence_event = occurrence_event.any()
        self._values_ds["occurrence_event"] = occurrence_event

        self._values_ds["weatherVarName"] = ("tmp", [risk_da.name])

        if "extrema" in self.compute_list or "representative" in self.compute_list:
            try:
                self._values_ds["units"] = ("tmp", [self.plain.units])
            except AttributeError:
                self._values_ds["units"] = ("tmp", [self.mountain.units])

        return new_risk_da > 0


class EventBertrandComposite(EventComposite):
    """Create an Element object containing the configuration of the Bertrand event
    for the promethee production task.

    Args:
        baseModel: Model from the pydantic library.

    Returns:
        baseModel: Element object.
    """

    process: str = PydanticField("Bertrand", const=True)
    field_1: FieldComposite
    cum_period: int

    @property
    def field_da(self) -> Optional[xr.DataArray]:
        """Get the values dataset.

        Returns:
            Optional[xr.DataArray]: Values dataset.
        """
        if self._field_da is None:
            field_da = super().field_da
            rr1_da = self.field_1.compute()

            if field_da.GRIB_stepUnits != rr1_da.GRIB_stepUnits:
                raise ValueError(
                    "Both cumulative fields do not have the same stepUnits. "
                    f"Simple field is {field_da.GRIB_stepUnits} and "
                    f"cumulField is {rr1_da.GRIB_stepUnits}."
                )

            # Divide the time over which cumulations are taken by the step size.
            # This yields a properly defined risk.
            n = int(self.cum_period / rr1_da.accum_hour)
            max_p = field_da[self.time_dimension].size
            if n < max_p:
                max_p = n

            self._field_da = field_da.rolling(
                {self.time_dimension: max_p}, min_periods=1
            ).max()
            self._field_da.attrs.update(field_da.attrs)
            self._field_da.name = field_da.name

        return self._field_da

    def get_risk(
        self,
        field_da: xr.DataArray,
        threshold: Threshold,
    ) -> xr.DataArray:
        """Calculate the risk for cumulative events such as Rainfall.

        Args:
            field_da: The field (RRn in the future).
            threshold: The threshold for the "bertrand" event.
            mask_da: The mask

        Returns:
            xr.DataArray: The calculated risk.
        """
        rr1_da = self.field_1.compute()
        if field_da.GRIB_stepUnits != rr1_da.GRIB_stepUnits:
            raise ValueError(
                "Both cumulative fields do not have the same stepUnits. "
                f"Simple field is {field_da.GRIB_stepUnits} and "
                f"cumulField is {rr1_da.GRIB_stepUnits}."
            )

        if self.compute_aggregated_values:
            agg_handler = Aggregator(rr1_da)
            rr1_da = agg_handler.compute(self.aggregation)

        # Replace n with the maximum dataset size. Otherwise, we cannot take the
        # maximum. Divide the time over which cumulations are taken by the step size.
        # This yields a properly defined risk.
        n = int(self.cum_period / rr1_da.accum_hour)

        start = operator.and_(
            threshold.comparison_op(field_da, threshold.threshold),
            threshold.comparison_op(rr1_da, threshold.threshold / n),
        )
        keep = operator.and_(
            threshold.comparison_op(field_da, threshold.threshold),
            threshold.comparison_op(self.field.compute(), threshold.threshold / n),
        )
        risk = start.copy()

        for step in range(len(risk[self.time_dimension].values)):
            if step > 0:
                current_risk = operator.or_(
                    risk.isel({self.time_dimension: step - 1})
                    * keep.isel({self.time_dimension: step}),
                    start.isel({self.time_dimension: step}),
                )
                risk.isel({self.time_dimension: step})[:] = current_risk[:]

        risk.attrs.update(rr1_da.attrs)
        return xr.where(field_da.notnull(), risk, np.nan)

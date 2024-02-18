from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, validator

import mfire.utils.mfxarray as xr
from mfire.composite.aggregations import (
    Aggregation,
    AggregationMethod,
    AggregationType,
    Aggregator,
)
from mfire.composite.base import BaseComposite
from mfire.composite.events import EventBertrandComposite, EventComposite
from mfire.composite.operators import LogicalOperator
from mfire.settings import get_logger
from mfire.utils.xr_utils import ArrayLoader, Loader, MaskLoader

# Logging
LOGGER = get_logger(name="levels.mod", bind="level")


class LocalisationConfig(BaseModel):
    """
    Class containing information related to location.
    """

    compass_split: bool = False
    altitude_split: bool = False
    geos_descriptive: List[str] = []


class LevelComposite(BaseComposite):
    """
    Represents a LevelComposite object containing the configuration of levels for the
    Promethee production task.

    Args:
        baseModel: BaseModel from the pydantic library.

    Returns:
        baseModel: LevelComposite object.
    """

    class Config:
        copy_on_model_validation = False

    level: int
    aggregation_type: AggregationType
    aggregation: Optional[Aggregation]
    logical_op_list: List[LogicalOperator] = []
    probability: str
    elements_event: List[Union[EventBertrandComposite, EventComposite]]
    time_dimension: Optional[str]
    compute_list: List[str] = []
    localisation: LocalisationConfig
    _spatial_risk_da: xr.DataArray = xr.DataArray()
    _mask: Optional[xr.MaskAccessor] = None

    @validator("aggregation")
    def check_aggregation(cls, v, values):
        """
        Validates the aggregation value based on the aggregation_type.

        Args:
            v: Input aggregation value.
            values: Input values.

        Returns:
            The validated aggregation value.

        Raises:
            ValueError: If the aggregation is missing and the aggregation_type is not
                AggregationType.UP_STREAM.
        """
        if values.get("aggregation_type") == AggregationType.UP_STREAM:
            return None
        if v is None:
            raise ValueError("Missing expected value 'aggregation' in level")
        return v

    @validator("elements_event")
    def check_nb_elements(cls, v, values):
        """
        Validates the number of elements in elements_event based on the
        aggregation_type.

        Args:
            v: Input elements_event value.
            values: Input values.

        Returns:
            The validated elements_event value.

        Raises:
            ValueError: If the number of logical operators is not consistent with the
            number of elements in the case of AggregationType.UP_STREAM.
        """
        if values.get("aggregation_type") == AggregationType.UP_STREAM:
            logical_op_list = values.get("logical_op_list") or []
            if len(logical_op_list) != len(v) - 1:
                raise ValueError(
                    "The number of logical operator is not consistent with the len "
                    f"of element list. Should be {len(v)-1}."
                )
        return v

    @property
    def mask(self) -> Optional[xr.MaskAccessor]:
        """
        Computes and returns the mask data array.

        Returns:
            xr.DataArray: Mask data array.
        """
        if self._mask is None and self.elements_event:
            self._mask = xr.MaskAccessor.make_union(
                *(evt.mask for evt in self.elements_event)
            )
        return self._mask

    @property
    def spatial_risk_da(self) -> xr.DataArray:
        """
        Returns the spatial risk data array.

        Returns:
            xr.DataArray: Spatial risk data array.
        """
        return self._spatial_risk_da

    @property
    def _cached_attrs(self) -> dict:
        """
        Returns the cached attributes.

        Returns:
            dict: Cached attributes.
        """
        return {
            "data": Loader,
            "spatial_risk_da": ArrayLoader,
        }

    def _compute(self, **_kwargs) -> xr.Dataset:
        """
        Computes the risk for a level.

        Returns:
            xr.Dataset: Output dataset containing the computed risk.
        """
        LOGGER.bind(level=self.level, composite_hash=self.hash)
        LOGGER.debug("Launching level.compute_risk")
        output_ds = self._compute_risk()
        LOGGER.debug("level.compute_risk done")
        LOGGER.try_unbind("level", "composite_hash")
        return output_ds

    @property
    def alt_min(self) -> int:
        """
        Returns the minimum altitude among all events.

        Returns:
            int: Minimum altitude.
        """
        return min(
            ev.altitude.alt_min for ev in self.elements_event if ev.altitude is not None
        )

    @property
    def alt_max(self) -> int:
        """
        Returns the maximum altitude among all events.

        Returns:
            int: Maximum altitude.
        """
        return max(
            ev.altitude.alt_max for ev in self.elements_event if ev.altitude is not None
        )

    @property
    def cover_period(self) -> xr.DataArray:
        """
        Returns the cover period of the first event.

        Returns:
            xr.DataArray: Cover period of the first event.
        """
        return self.elements_event[0].cover_period

    @property
    def is_bertrand(self) -> bool:
        """
        Checks if all events in the list are of type EventBertrandComposite.

        Returns:
            bool: True if all events are of type EventBertrandComposite,
                False otherwise.
        """
        return all(
            isinstance(event, EventBertrandComposite) for event in self.elements_event
        )

    def get_single_evt_comparison(self) -> Optional[Dict]:
        """
        Gets the comparison operator for a single event.

        Returns:
            Union[dict, None]: A list of comparison operators for a single event.
                None if there are multiple events.
        """
        return self.elements_event[0].get_comparison()

    def get_comparison(self) -> dict:
        """
        Gets the comparison operators for a level.

        Returns:
            dict: Dictionary of comparison operators (on plain or mountain).

        Raises:
            ValueError: If the comparison operators for different fields are different.
        """
        dout = {}
        for event in self.elements_event:
            field_name = event.field.name
            comparison = event.get_comparison()
            if field_name is not None and field_name not in dout:
                dout[field_name] = comparison
            elif field_name in dout and dout[field_name] != comparison:
                LOGGER.error(
                    f" Current  {dout[field_name]} is different of new one "
                    f"{comparison}. Don't know what to do in this case. "
                )
        return dout

    def update_selection(
        self,
        new_sel: Optional[dict] = None,
        new_slice: Optional[dict] = None,
        new_isel: Optional[dict] = None,
        new_islice: Optional[dict] = None,
    ):
        """
        Updates the selection for all events.

        Args:
            new_sel: Selection dictionary.
            new_slice: Slice dictionary.
            new_isel: isel dictionary.
            new_islice: islice dictionary.
        """
        if new_sel is None:
            new_sel = {}
        if new_slice is None:
            new_slice = {}
        if new_isel is None:
            new_isel = {}
        if new_islice is None:
            new_islice = {}
        for element in self.elements_event:
            element.update_selection(
                new_sel=new_sel,
                new_slice=new_slice,
                new_isel=new_isel,
                new_islice=new_islice,
            )

    @property
    def grid_name(self) -> str:
        """
        Returns the grid name.

        Returns:
            str: Grid name.
        """
        return self.elements_event[0].field.grid_name

    @property
    def geos_file(self) -> Path:
        """
        Returns the geos file.

        Returns:
            Path: Geos file.
        """
        return self.elements_event[0].geos.file

    @property
    def geos_descriptive(self) -> xr.DataArray:
        """
        Returns the descriptive geos.

        Returns:
            xr.DataArray: Descriptive geos.
        """
        return MaskLoader(filename=self.geos_file, grid_name=self.grid_name).load(
            ids_list=self.localisation.geos_descriptive
        )

    def _compute_risk(self) -> xr.Dataset:
        """
        Computes the risk for a level.
        This function combines different events.
        The output dataset is not generated here, only the risk is calculated.

        Returns:
            xr.Dataset: Output dataset containing the computed risk.
        """
        output_ds = xr.Dataset()

        # 1. computing all events and retrieving results for output
        events = []
        for i, event in enumerate(self.elements_event):
            events.append(event.compute())
            tmp_ds = event.values_ds.expand_dims(dim="evt").assign_coords(evt=[i])
            output_ds = xr.merge([output_ds, tmp_ds])

        # 2. combining all events using logical operators
        risk_da = LogicalOperator.apply(self.logical_op_list, events)
        self._spatial_risk_da = risk_da * self.mask.f32

        # 3. aggregating if necessary
        aggregation = self.aggregation
        if aggregation is not None:
            agg_handler = Aggregator(self._spatial_risk_da)

            # Adding to have the combined event density as output
            if "density" in self.compute_list:
                output_ds["risk_density"] = agg_handler.compute(
                    Aggregation(method=AggregationMethod.DENSITY)
                )
                output_ds["risk_density"].attrs = {}

            if "summary" in self.compute_list:
                agg_handler_time = Aggregator(
                    risk_da, aggregate_dim=self.time_dimension
                )
                max_risk_da = (
                    agg_handler_time.compute(Aggregation(method=AggregationMethod.MAX))
                    * self.mask.f32
                )
                agg_handler_space = Aggregator(max_risk_da)
                output_ds["risk_summarized_density"] = agg_handler_space.compute(
                    Aggregation(method=AggregationMethod.DENSITY)
                )
                output_ds["risk_summarized_density"].attrs = {}

            # Calculating the risk occurrence
            risk_da = agg_handler.compute(aggregation)

        output_ds["occurrence"] = risk_da > 0
        output_ds["occurrence"].attrs = {}

        # Clean useless attributes
        self._spatial_risk_da.attrs = {}

        # Checking if the variables are present
        for coord in ("areaName", "areaType"):
            if coord not in output_ds.coords:
                output_ds.coords[coord] = ("id", ["unknown"] * output_ds.id.size)
        return output_ds.squeeze("tmp")

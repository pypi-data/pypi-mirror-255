from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, validator

import mfire.utils.mfxarray as xr
from mfire.composite.components import RiskComponentComposite
from mfire.composite.events import Category
from mfire.settings import get_logger
from mfire.utils.date import Datetime
from mfire.utils.xr_utils import compute_step_size

LOGGER = get_logger(name="cdp.datasets.mod", bind="cdp.datesets")


class CDPParam(BaseModel):
    """Creates a Param object containing the Param configuration."""

    Name: str
    Stepsize: Optional[int]


class CDPValueParam(BaseModel):
    """Creates a ValuesWithParam object containing the ValuesWithParam configuration.

    Attributes:
        ValueType: The type of the value.
        Unit: The unit of the value.
        Value: The value itself.
        Param: An optional Param object.
    """

    ValueType: str
    Unit: str
    Value: float
    Param: Optional[CDPParam]

    @classmethod
    def from_composite(
        cls, evt_only_ds: xr.Dataset, stepsize: Optional[int] = None
    ) -> List[CDPValueParam]:
        """
        Extracts the extractable information (with respect to the specs) for the CDP
        from a dataset (for a given level and area).

        Args:
            ds (xr.dataset): Dataset with only 'evt' as dimension.
            stepsize (int, optional) : model stepsize for this parameter at this
                deadline.

        Returns:
            List[CDPValueParam]: A list of `CDPValueParam` objects containing the
            extractable information.
        """
        # Check that the dataset has only the 'evt' dimension
        if (set_dims := set(evt_only_ds.dims)) != {"evt"}:
            raise ValueError(
                "In CDPValueParam.from_composite we expect ds to have only "
                f"'evt' as dimension. However we get {set_dims}."
            )

        # Drop null events.
        my_ds = evt_only_ds.dropna("evt", how="all")

        # Find empty variables.
        empty = {var for var in my_ds if my_ds[var].count() == 0}

        # Drop useless variables.
        useless = {
            "areaName",
            "areaType",
            "occurrence_event",
            "weatherVarName",
            "risk_density",
            "risk_summarized_density",
            "units",
        }

        # Find variables that can appear in the output.
        variables = sorted(set(my_ds.data_vars).difference(empty).difference(useless))

        # Create a list of `CDPValueParam` objects.
        values_list = []
        for var in variables:
            if my_ds[var].size > 1:
                LOGGER.debug(
                    f"Too many information to go the CDP for variable {var}",
                    var=var,
                    func="CDPValueParam.from_composite",
                )
                continue
            if var in (
                "occurrence",
                "density",
                "summarized_density",
                "risk_density",
                "risk_summarized_density",
            ):
                unit = "1"
                param = None
            else:
                # Case of values on plains/mountains etc..
                # The returns are made in the units that
                # have been specified to us for the threshold.
                if "units" in my_ds:
                    unit = my_ds["units"].values[0]
                else:
                    unit = "unknown"
                param = CDPParam(
                    Name=my_ds["weatherVarName"].values[0],
                    Stepsize=stepsize,
                )

            values_list.append(
                cls(
                    ValueType=var,
                    Value=round(float(my_ds[var]), 2),
                    Unit=unit,
                    Param=param,
                )
            )

        return values_list


class CDPSummary(BaseModel):
    """A class that represents a CDP summary.

    Attributes:
        ValidityDate: The validity date of the summary, or `None` if the summary is not
            time-bound.
        Level: The level of the summary.
        Values: A list of `CDPValueParam` objects, each representing a value in the
            summary.
    """

    ValidityDate: Optional[Datetime]
    Level: int
    Values: List[CDPValueParam]

    @validator("ValidityDate", pre=True)
    def init_dates(cls, val: str) -> Datetime:
        return Datetime(val) if val is not None else None

    @classmethod
    def from_composite(
        cls, component: RiskComponentComposite, geo_id: str
    ) -> CDPSummary:
        """Returns a Short Summary (not on every step but on the whole period)

        Args:
            component: The RisksComponent object to be converted.
            geo_id: The identifier of the geographic area.

        Returns:
            CDPSummary: CDPSummary of the whole component.
        """
        tmp_ds = component.risks_ds.sel(id=geo_id)
        time_dim = component.time_dimension
        final_level_da = component.final_risk_da.sel(id=geo_id)
        level = final_level_da.max()

        # Selects the lowest level, even if no level is activated.
        if level > 0:
            summary_level = level
            dmax, *_ = xr.align(
                tmp_ds.sel(risk_level=summary_level),
                final_level_da.wheretype.f32(
                    final_level_da == summary_level, drop=True
                ),
            )
        else:
            summary_level = tmp_ds.risk_level.min()
            dmax = tmp_ds.sel(risk_level=summary_level)

        # Determines what variables to return.
        level_ds = dmax.drop_vars(
            ("areaName", "areaType"),
            errors="ignore",
        ).mean(time_dim)

        # Handles specific cases for some variables.
        for var in dmax.data_vars:
            if "max" in var:
                level_ds[var] = dmax[var].max(time_dim)
            if "min" in var:
                level_ds[var] = dmax[var].min(time_dim)

        # Handles specific cases for representative values.
        risk_level = component.risks_of_level(level=summary_level)
        dict_comparison = risk_level[0].get_single_evt_comparison()
        if dict_comparison is not None:
            for key in dict_comparison:
                rep_key = "rep_value_" + key
                if rep_key in level_ds and dict_comparison.get("category") in (
                    Category.QUANTITATIVE,
                    Category.RESTRICTED_QUANTITATIVE,
                ):
                    level_ds[rep_key] = dict_comparison[
                        key
                    ].comparison_op.critical_value(
                        dmax[rep_key], dim=component.time_dimension
                    )

        # Renames some variables.
        for var in ("summarized_density", "risk_summarized_density"):
            if var in dmax.data_vars:
                level_ds["density"] = dmax[var]
                level_ds = level_ds.drop_vars(var)

        # Ensures that occurrence is True.
        if level > 0:
            level_ds["occurrence"] = True

        return CDPSummary(Level=level, Values=CDPValueParam.from_composite(level_ds))

    @classmethod
    def list_from_composite(
        cls, component: RiskComponentComposite, geo_id: str
    ) -> List[CDPSummary]:
        """Returns a summary of all computed values at every step of the given
        component.

        Args:
            component (RiskComponentComposite): RiskComponentComposite to summarize.
            geo_id (str): Geographical's id of the area to summarize.

        Returns:
            List[CDPSummary]: List of CDPSummary for each step.
        """
        risks_ds = component.risks_ds.sel(id=geo_id).drop_vars(
            ("summarized_density", "risk_summarized_density"), errors="ignore"
        )
        time_dim = component.time_dimension
        stepsize_da = compute_step_size(risks_ds, coord_name=time_dim)
        data_list = []
        for step in risks_ds[time_dim]:
            level = component.final_risk_da.sel({"id": geo_id, time_dim: step}).values
            summary_level = level if level > 0 else risks_ds.risk_level.min().values
            data_list.append(
                cls(
                    ValidityDate=step,
                    Level=level,
                    Values=CDPValueParam.from_composite(
                        risks_ds.sel({time_dim: step, "risk_level": summary_level}),
                        stepsize=int(stepsize_da.sel({time_dim: step}).values),
                    ),
                )
            )
        return data_list


class CDPDataset(BaseModel):
    """
    A class that represents a CDP dataset.

    Attributes:
    ShortSummary: A CDPSummary object that provides a brief overview of the dataset.
    Summary: A list of CDPSummary objects, each representing a summary of the data at
        a different level of granularity.
    """

    ShortSummary: CDPSummary
    Summary: List[CDPSummary]

    @classmethod
    def from_composite(
        cls, component: RiskComponentComposite, geo_id: str
    ) -> CDPDataset:
        if component.is_risks_empty:
            return CDPDataset(ShortSummary=CDPSummary(Level=0, Values=[]), Summary=[])

        return CDPDataset(
            ShortSummary=CDPSummary.from_composite(component=component, geo_id=geo_id),
            Summary=CDPSummary.list_from_composite(component=component, geo_id=geo_id),
        )

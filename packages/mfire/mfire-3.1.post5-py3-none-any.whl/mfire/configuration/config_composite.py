"""
@package configuration.functions

functions for Config processor module
"""
from pathlib import Path

from mfire import composite

# Own package
from mfire.settings import get_logger

# Third parties package


# local package

# Logging
LOGGER = get_logger(name="config_processor.mod", bind="config_functions")


def get_new_threshold(threshold: dict) -> composite.Threshold:
    return composite.Threshold(
        threshold=threshold["threshold"],
        comparison_op=threshold["comparisonOp"],
        units=threshold["units"],
    )


def get_aggregation(
    aggregation: dict,
    mask_file: Path,
    grid_name: str = "",
) -> composite.Aggregation:
    kwargs = aggregation.get("kwargs")
    if kwargs is None:
        return composite.Aggregation(**aggregation)
    # Filling new kwargs
    new_kwargs = dict()

    # dr: float
    if "dr" in kwargs:
        new_kwargs["dr"] = kwargs["dr"]
    elif "drConditional" in kwargs:
        new_kwargs["dr"] = kwargs["drConditional"]
    elif "drCentralZone" in kwargs:
        new_kwargs["dr"] = kwargs["drCentralZone"]
    new_kwargs["dr"] = float(new_kwargs["dr"])
    if new_kwargs["dr"] > 1 and new_kwargs["dr"] <= 100:
        new_kwargs["dr"] = new_kwargs["dr"] / 100.0

    # central_weight: Optional[int]
    if "centralWeight" in kwargs:
        new_kwargs["central_weight"] = kwargs["centralWeight"]

    # outer_weight: Optional[int]
    if "outerWeight" in kwargs:
        new_kwargs["outer_weight"] = kwargs["outerWeight"]

    # central_mask_id: Optional[GeoComposite]
    for central_key in ("centralZone", "centralZoneConditional"):
        central_mask = kwargs.get(central_key)
        if central_mask is not None:
            new_kwargs["central_mask"] = composite.GeoComposite(
                file=mask_file,
                mask_id=central_mask,
                grid_name=grid_name,
            )
    return composite.Aggregation(method=aggregation["method"], kwargs=new_kwargs)

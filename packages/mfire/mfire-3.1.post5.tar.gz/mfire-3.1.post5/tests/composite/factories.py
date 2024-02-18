from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

import numpy as np

import mfire.utils.mfxarray as xr
from mfire.composite import (
    Aggregation,
    AggregationType,
    AltitudeComposite,
    BaseComposite,
    ComparisonOperator,
    EventBertrandComposite,
    FieldComposite,
    GeoComposite,
    LevelComposite,
    LocalisationConfig,
    LogicalOperator,
    Period,
    ProductionComposite,
    RiskComponentComposite,
    WeatherComposite,
)
from mfire.composite.aggregations import AggregationMethod
from mfire.composite.components import TextComponentComposite
from mfire.composite.events import Category, EventComposite, Threshold
from mfire.settings import SETTINGS_DIR
from mfire.utils.date import Datetime


class PeriodFactory(Period):
    id: str = "period_id"
    name: Optional[str] = "period_name"
    start: Datetime = Datetime(2023, 3, 1)
    stop: Datetime = Datetime(2023, 3, 5)


class AggregationFactory(Aggregation):
    method: AggregationMethod = AggregationMethod.MEAN
    kwargs: dict = {}


class BaseCompositeFactory(BaseComposite):
    """Base composite factory class."""

    def __init__(
        self, data: Optional[Union[xr.DataArray, xr.Dataset]] = None, **kwargs
    ):
        """Initialize the base composite factory.

        Args:
            data: Result value.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self._data = data
        self._keep_data = True


class ProductionCompositeFactory(BaseCompositeFactory, ProductionComposite):
    id: str = "production_id"
    name: str = "production_name"
    config_hash: str = "production_config_hash"
    prod_hash: str = "production_hash"
    mask_hash: str = "production_mask_hash"
    components: List[Union[RiskComponentComposite, TextComponentComposite]] = []


class FieldCompositeFactory(
    BaseCompositeFactory,
    FieldComposite,
):
    """Field composite factory class."""

    file: Union[Path, List[Path]] = Path("field_composite_path")
    grid_name: str = "franxl1s100"
    name: str = "field_name"


class GeoCompositeFactory(BaseCompositeFactory, GeoComposite):
    """Geo composite factory class."""

    file: Path = Path("geo_composite_file")
    mask_id: Union[List[str], str] = "mask_id"
    grid_name: Optional[str] = "franxl1s100"


class AltitudeCompositeFactory(BaseCompositeFactory, AltitudeComposite):
    """Altitude composite factory class."""

    filename = Path(SETTINGS_DIR / "geos/altitudes/franxl1s100.nc")
    grid_name = "franxl1s100"
    name = "name"


class EventCompositeFactory(BaseCompositeFactory, EventComposite):
    """Factory class for creating EventComposite objects."""

    field: FieldComposite = FieldCompositeFactory(None)
    category: Category = Category.BOOLEAN
    altitude: AltitudeComposite = AltitudeCompositeFactory()
    geos: Union[GeoComposite, xr.DataArray] = GeoCompositeFactory()
    time_dimension: Optional[str] = "valid_time"
    plain: Optional[Threshold] = Threshold(
        threshold=20, comparison_op=ComparisonOperator.SUPEGAL, units="mm"
    )
    aggregation: Optional[Aggregation] = AggregationFactory()
    aggregation_aval: Optional[Aggregation] = None


class EventBertrandCompositeFactory(EventCompositeFactory, EventBertrandComposite):
    """Factory class for creating EventBertrandComposite objects."""

    field_1 = FieldCompositeFactory(None)
    cum_period = 6


class LevelCompositeFactory(BaseCompositeFactory, LevelComposite):
    level: int = 2
    aggregation: Optional[Aggregation] = None
    aggregation_type: AggregationType = AggregationType.UP_STREAM
    probability: str = "no"
    elements_event: List[Union[EventBertrandComposite, EventComposite]] = [
        EventCompositeFactory()
    ]
    time_dimension: Optional[str] = "valid_time"
    localisation: LocalisationConfig = LocalisationConfig()

    def __init__(self, **data: Any):
        elements_event = data.get("elements_event")
        if elements_event is not None and data.get("logical_op_list") is None:
            logical_ops = [op.value for op in LogicalOperator]
            data["logical_op_list"] = list(
                np.random.choice(logical_ops, size=len(elements_event) - 1)
            )
        super().__init__(**data)


class TextComponentCompositeFactory(BaseCompositeFactory, TextComponentComposite):
    period = PeriodFactory()
    id: str = "text_component_id"
    name: str = "text_component_name"
    production_id: str = "production_id"
    production_name: str = "production_name"
    production_datetime: Datetime = Datetime(2023, 3, 1, 6)

    weathers: List[WeatherComposite] = []
    product_comment: bool = True

    customer_id: Optional[str] = "customer_id"
    customer_name: Optional[str] = "customer_name"


class RiskComponentCompositeFactory(BaseCompositeFactory, RiskComponentComposite):
    period: Period = PeriodFactory()
    id: str = "risk_component_id"
    name: str = "risk_component_name"
    production_id: str = "production_id"
    production_name: str = "production_name"
    production_datetime: Datetime = Datetime(2023, 3, 1, 6)

    levels: List[LevelComposite] = []
    hazard_id: str = "hazard_id"
    hazard_name: str = "hazard_name"
    product_comment: bool = True

    customer_id: Optional[str] = "customer_id"
    customer_name: Optional[str] = "customer_name"


class WeatherCompositeFactory(BaseCompositeFactory, WeatherComposite):
    id: str = "id_weather"
    params: Dict[str, FieldComposite] = {}
    units: Dict[str, Optional[str]] = {}
    localisation: LocalisationConfig = LocalisationConfig()

    geos_descriptive_factory: Optional[xr.DataArray] = None
    altitudes_factory: Optional[xr.DataArray] = None

    def geos_descriptive(self, geo_id: str) -> xr.DataArray:
        if self.geos_descriptive_factory is None:
            return super().geos_descriptive(geo_id)
        return self.geos_descriptive_factory

    def altitudes(self, param: str) -> Optional[xr.DataArray]:
        if self.altitudes_factory is None:
            return super().altitudes(param)
        return self.altitudes_factory

    @classmethod
    def create_factory(
        cls,
        geos_descriptive: list,
        valid_times: list,
        lon: list,
        lat: list,
        data_vars: dict,
        altitude: Optional[list],
        **kwargs,
    ) -> WeatherComposite:
        data_ds = xr.Dataset(
            data_vars=data_vars,
            coords={
                "id": "id_axis",
                "valid_time": valid_times,
                "latitude": lat,
                "longitude": lon,
            },
        )

        ids = list(map(str, list(range(len(geos_descriptive)))))
        compo = cls(
            data=data_ds,
            production_datetime=data_ds.valid_time[0],
            **kwargs,
            geos_descriptive_factory=xr.DataArray(
                data=geos_descriptive,
                dims=["id", "latitude", "longitude"],
                coords={
                    "id": ids,
                    "latitude": lat,
                    "longitude": lon,
                    "areaType": (["id"], ["Axis"] + (len(ids) - 1) * [""]),
                    "areaName": (
                        ["id"],
                        [f"à localisation N°{i+1}" for i in range(len(ids))],
                    ),
                },
            ),
            altitudes_factory=xr.DataArray(
                data=altitude,
                dims=["latitude", "longitude"],
                coords={
                    "latitude": lat,
                    "longitude": lon,
                },
            ),
        )

        compo.geos = (
            compo.geos_descriptive_factory.sum(dim="id").expand_dims(
                {"id": ["id_axis"]}
            )
            > 0
        )
        return cast(WeatherComposite, compo)

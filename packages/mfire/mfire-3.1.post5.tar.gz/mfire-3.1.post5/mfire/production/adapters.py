from abc import ABC, abstractmethod

from mfire.composite import RiskComponentComposite, TextComponentComposite
from mfire.composite.components import TypeComponent
from mfire.production.base import BaseCDPAdapter
from mfire.production.components import CDPComponents, CDPRisk, CDPText
from mfire.production.productions import CDPProduction
from mfire.settings import get_logger
from mfire.utils.date import Datetime

LOGGER = get_logger(name="output_adapter.mod", bind="output_adapter")


class CDPAdapter(BaseCDPAdapter):
    """Class to be used for the implementation of an adapter taking a risk or text
    component
    """

    def compute(self) -> CDPProduction:
        """Computes the adapted components.

        Returns:
            A list of CDPComponents, one for each geo_id.
        """
        adapter_class = (
            CDPTextAdapter
            if self.component.type == TypeComponent.TEXT
            else CDPRiskAdapter
        )
        return adapter_class(component=self.component, texts=self.texts).compute()


class AbstractCDPSynthesisAdapter(BaseCDPAdapter, ABC):
    @property
    @abstractmethod
    def adapted_components(self) -> CDPComponents:
        """Returns a list of CDPComponents."""

    def compute(self) -> CDPProduction:
        return CDPProduction(
            ProductionId=self.component.production_id,
            ProductionName=self.component.production_name,
            CustomerId=self.component.customer_id,
            CustomerName=self.component.customer_name,
            DateBulletin=self.component.production_datetime,
            DateProduction=Datetime.now(),
            DateConfiguration=self.component.configuration_datetime,
            Components=self.adapted_components,
        )


class CDPRiskAdapter(AbstractCDPSynthesisAdapter):
    component: RiskComponentComposite

    @property
    def adapted_components(self) -> CDPComponents:
        """Returns a list of CDPRisks."""
        return CDPComponents(
            Aleas=[
                CDPRisk.from_composite(
                    component=self.component,
                    geo_id=geo_id,
                    text=self.texts[geo_id],
                )
                for geo_id in self.texts
            ]
        )


class CDPTextAdapter(AbstractCDPSynthesisAdapter):
    component: TextComponentComposite

    @property
    def adapted_components(self) -> CDPComponents:
        """Returns a list of CDPRisks."""
        return CDPComponents(
            Text=[
                CDPText.from_composite(
                    component=self.component,
                    geo_id=geo_id,
                    text=self.texts[geo_id],
                )
                for geo_id in self.texts
            ]
        )

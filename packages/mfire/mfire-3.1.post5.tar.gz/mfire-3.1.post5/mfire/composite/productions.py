from __future__ import annotations

from typing import List, Union

from mfire.composite.base import BaseComposite
from mfire.composite.components import RiskComponentComposite, TextComponentComposite
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="productions.mod", bind="productions")


class ProductionComposite(BaseComposite):
    """
    Represents a ProductionComposite object containing the configuration of the
    Promethee production task.

    Args:
        baseModel: Pydantic base model.

    Returns:
        baseModel: Production object.
    """

    id: str
    name: str
    config_hash: str
    prod_hash: str
    mask_hash: str
    components: List[Union[RiskComponentComposite, TextComponentComposite]]

    def _compute(self, **_kwargs):
        """
        Computes the production task by iterating over the components and invoking
        their compute method.
        """
        for component in self.components:
            component.compute()

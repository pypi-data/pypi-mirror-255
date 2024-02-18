from functools import partial
from typing import Any, Optional

from pydantic import BaseModel

import mfire.utils.mfxarray as xr
from mfire.composite import RiskComponentComposite
from mfire.settings import get_logger
from mfire.text.comment import Reducer
from mfire.text.comment.monozone import Monozone
from mfire.text.comment.multizone import new_multizone

# Logging
LOGGER = get_logger(name="manager.mod", bind="manager")

xr.set_options(keep_attrs=True)


class Manager(BaseModel):
    """Module for managing comment generation.
    This module decides which text generation module to use."""

    selector: Any
    reducer: Optional[Reducer]
    builder: Any

    def build_monozone(self, component: RiskComponentComposite, geo_id: str) -> str:
        """Generate the comment for a monozone type.

        Args:
            component (RiskComponentComposite): The risk component being studied.
            geo_id (str): The ID of the zone.

        Returns:
            str: The detailed comment.
        """
        self.reducer.reduce_monozone(geo_id)
        self.builder = Monozone(self.reducer.reduction["template"])

        comment = self.builder.compute(self.reducer.reduction)

        return comment

    def compute(
        self,
        geo_id: str,
        component: RiskComponentComposite,
    ) -> str:
        """
        Retrieve the comment for the identified zone.
        This function requires that the decision_tree has been triggered beforehand.

        Args:
            geo_id (str): The ID of the zone.
            component (RiskComponentComposite): The risk component.

        Returns:
            str: The comment.
        """
        self.reducer = Reducer(component=component)
        self.reducer.compute(geo_id, component)

        if self.reducer.module == "monozone":
            self.builder = Monozone(self.reducer.reduction["template"])
        else:
            template_name = self.reducer.reduction.get_template_type()
            self.builder = new_multizone(
                template_name,
                monozone_access=partial(self.build_monozone, geo_id=geo_id),
            )

        return self.builder.compute(self.reducer.reduction)

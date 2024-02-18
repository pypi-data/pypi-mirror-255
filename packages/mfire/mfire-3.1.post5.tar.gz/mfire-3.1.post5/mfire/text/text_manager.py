from typing import Optional, Union
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from mfire.composite.components import RiskComponentComposite, TextComponentComposite
from mfire.settings import get_logger
from mfire.text.comment import Manager
from mfire.text.factory import DirectorFactory
from mfire.utils.date import Timedelta

LOGGER = get_logger(name="text_manager.mod", bind="text_manager")


class TextManager(BaseModel):
    """Class for dispatching the text generation according to the given composite's
    type.

    Args:
        component (Union[RiskComponentComposite, TextComponentComposite]) :
            Component to produce a text with.
    """

    component: Union[RiskComponentComposite, TextComponentComposite]
    _reduction: Optional[dict] = None  # temporary reduction attr for sit_gen usage

    class Config:
        """Cette classe Config permet de contrôler de comportement de pydantic"""

        underscore_attrs_are_private = True

    def compute_sit_gen(self, geo_id: str = None) -> str:
        """Temporary method for producing the

        Args:
            geo_id (str, optional): _description_. Defaults to None.

        Returns:
            str: _description_
        """
        # It is really really bad practice to import elsewhere than the top of the file
        # BUT one of those imports depends on TensorFlows/Keras end is sloooooooow
        # (We are talking ~5s load time, it basically doubles the compute time of a
        # composite). Since the ovewhelming majority of the productions dont need
        # those imports, we skip them until we need them and our HPC cpu use time
        # is cut in half. If someone got a better way to do this, fell free to do so :)
        from mfire.text.sit_gen import SitGenBuilder, SitGenReducer

        if self._reduction is None:
            self._reduction = SitGenReducer().compute(self.component)
        builder = SitGenBuilder()
        builder.compute(self._reduction[geo_id])
        return builder._text

    def compute(self, geo_id: str = None) -> str:
        """Produce a text according to the given self.composite's type.

        Args:
            geo_id (str, optional): Optional geo_id for comment generation.
                Defaults to None.

        Returns:
            str: Text corresponding to the self.composite and the given geo_id.
        """
        if isinstance(self.component, TextComponentComposite):

            if self.component.weathers and all(
                w.id.startswith("sitgen") for w in self.component.weathers
            ):
                return self.compute_sit_gen(geo_id=geo_id)

            # Add the text title with the date
            # Currently we only use the Paris Timezone - see #36169
            zone_info = ZoneInfo("Europe/Paris")
            start = max(
                self.component.period.start,
                self.component.production_datetime + Timedelta(hours=1),
            ).astimezone(zone_info)
            stop = self.component.period.stop.astimezone(zone_info)
            my_text = (
                f"De {start.weekday_name} {start.strftime('%d')} à "
                f"{start.strftime('%H')}h jusqu'au {stop.weekday_name} "
                f"{stop.strftime('%d')} à {stop.strftime('%H')}h :\n"
            )
            for weather in self.component.weathers:
                director = DirectorFactory()
                my_text += director.compute(geo_id=geo_id, weather=weather) + "\n"
            return my_text

        manager = Manager()
        return manager.compute(geo_id=geo_id, component=self.component)

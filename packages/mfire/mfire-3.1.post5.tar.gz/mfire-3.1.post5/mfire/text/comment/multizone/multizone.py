from __future__ import annotations

from mfire.settings import TEMPLATES_FILENAMES, Settings, get_logger
from mfire.text.comment.multizone import ComponentInterface
from mfire.text.comment.multizone.comment_builder import (
    PeriodCommentBuilder,
    TemplateCommentBuilder,
    ZoneCommentBuilder,
)
from mfire.text.comment.representative_builder import RepresentativeValueManager
from mfire.text.template import read_template
from mfire.utils.string_utils import clean_french_text

# Logging
LOGGER = get_logger(name="text.comment.multizone.mod", bind="text.comment.multizone")


def new_multizone(template_name, monozone_access=None) -> MultiZone:
    """Create a new MultiZone comment builder object.

    Args:
        template_name (str): The name of the template.
        monozone_access (bool, optional): Monozone access flag. Defaults to None.

    Returns:
        MultiZone: A new MultiZone comment builder object.
    """
    key = "generic"
    if template_name == "SNOW":
        key = "snow"
    elif template_name == "PRECIP":
        key = "precip"
    return MultiZone(
        read_template(TEMPLATES_FILENAMES[Settings().language]["multizone"][key]),
        monozone_access=monozone_access,
    )


class MultiZone(
    TemplateCommentBuilder,
    PeriodCommentBuilder,
    ZoneCommentBuilder,
    RepresentativeValueManager,
):
    """MultiZone comment builder for handling 'multizone' types of components.

    Args:
        template_retriever (TemplateRetriever): Object that can find and provide
            a template corresponding to the component handler.

    Inheritance:
        TemplateCommentBuilder
        PeriodCommentBuilder
        ZoneCommentBuilder
    """

    def handle_area_problems(self, areaIds) -> None:
        """Handle area problems by modifying the template, retrieving the template,
        reprocessing the periods, and reprocessing the zones.

        Args:
            areaIds (list): List of area IDs.
        """
        LOGGER.debug(f"Function for handling area problems: {areaIds}")
        # 1. Modify the template
        self.component_handler.modify_template(areaIds)
        LOGGER.debug(f"Modified template: {self.component_handler.get_template_key()}")
        # 2. Retrieve the template again
        self.retrieve_template()
        # 3. Reprocess the periods
        self.process_period()
        # 4. Reprocess the zones
        self.process_zone(self.handle_area_problems)
        # The fifth step is performed after the previous process_zone
        # (which called handle_area_problems).

    def compute(self, component_handler: ComponentInterface) -> None:
        """Process the comment according to the given component handler.

        Args:
            component_handler (ComponentInterface): Object handling all the component's
                features necessary to create an appropriate comment.
        """
        self.reset()
        self.component_handler = component_handler
        self.retrieve_template()
        self.process_period()
        self.process_zone(self.handle_area_problems)
        self.process_rep_value(reduction={})

        return clean_french_text(self.text)

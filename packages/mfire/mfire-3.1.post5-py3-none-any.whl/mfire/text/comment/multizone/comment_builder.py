from __future__ import annotations

from itertools import combinations

from mfire.settings import get_logger
from mfire.text.base import BaseBuilder
from mfire.text.period_describer import PeriodDescriber
from mfire.text.template import TemplateRetriever
from mfire.utils.date import Period

# Logging
LOGGER = get_logger(name="text.comment_builder.mod", bind="text.comment_builder")


class TemplateCommentBuilder(BaseBuilder):
    """Comment Builder designed for Template retrieving tasks."""

    def __init__(self, template_retriever: TemplateRetriever, monozone_access):
        """Initialize TemplateCommentBuilder.

        Args:
            template_retriever (TemplateRetriever): Object that retrieves templates.
            monozone_access (partial function): Function to access the monozone module
                if the template is not found.
        """
        super().__init__()
        self.template_retriever = template_retriever
        self.monozone_access = monozone_access

    def retrieve_template(self):
        """Retrieve the template using template_retriever."""
        key = self.component_handler.get_template_key()
        default = f"Failed to retrieve template (key={key}) (error COM-001)."
        self.text = self.template_retriever.get(key=key, default=default)

        if self.text == default:
            if self.monozone_access is not None and key == "P1_1":
                # Pass to monozone module if template retrieval fails and key is "P1_1".
                LOGGER.warning(
                    "Passing through monozone after requesting template 'P1_1'.",
                    key=key,
                    **self.component_handler.log_ids,
                )
                self.text = self.monozone_access(
                    component=self.component_handler.localisation_handler.component
                )
            else:
                # Otherwise, it's an error.
                LOGGER.error(
                    f"Failed to retrieve template '{key}'.",
                    key=key,
                    **self.component_handler.log_ids,
                )
        else:
            LOGGER.info(
                f"Choosing template '{key}'", key=key, **self.component_handler.log_ids
            )


class PeriodCommentBuilder(BaseBuilder):
    """Comment Builder for processing period-related tags in a comment."""

    def process_period(self):
        """Process period-related tags in the comment."""
        request_time = self.component_handler.get_production_datetime()
        periods = []
        for period_name in self.component_handler.get_periods_name():
            time_list = period_name.split("_to_")
            periods += [Period(time_list[0], time_list[-1])]

        periods_table = {}
        elements = range(len(periods))

        for i in elements:
            for combin in combinations(elements, i + 1):
                keys, values = [], []
                for j in combin:
                    keys += [str(j + 1)]
                    values += [periods[j]]
                key = "periode" + "_".join(keys)
                if f"{{{key}}}" in self.text:
                    periods_table[key] = PeriodDescriber(request_time).describe(values)

        self.text = self.text.format(**periods_table)


class ZoneCommentBuilder(BaseBuilder):
    """Comment Builder for processing zone-related tags in a comment."""

    @staticmethod
    def handle_areaNameProblem(zones_table, zones, parent_function):
        """Handle the case where two zones have similar names.

        Args:
            zones_table (dict): Dictionary mapping zone names to their IDs.
            zones (list): List of zone IDs.
            parent_function (func): Function to resolve the issue.
        """
        zones_values = set(zones_table.values())
        LOGGER.debug(f"Zones in process_zone {zones_table}")
        ids = None

        for areaName in zones_values:
            tp_list = []
            for key in zones_table.keys():
                if zones_table[key] == areaName:
                    tp_list.append(key)
            if len(tp_list) > 1:
                num_list = []
                for zone in tp_list:
                    zone = zone.replace("zone", "")
                    num_list.extend(zone.split("_"))
                LOGGER.debug(f"Affected zones are {set(num_list)}")
                ids = [zones[int(num) - 1] for num in set(num_list)]
                LOGGER.debug(
                    f"We have an issue with {areaName} appearing in {tp_list}."
                )
                LOGGER.debug(
                    f"The zones causing this issue have the following IDs: {ids}"
                )
                break

        if parent_function is not None and ids is not None:
            LOGGER.warning(
                f"Calling parent class function to handle zone issue: {areaName}, {ids}"
            )
            parent_function(ids)
        else:
            LOGGER.error("Either parent func or ids is None. Get for ids {ids}.")

    def process_zone(self, parent_function=None):
        """Process zone-related tags in the comment."""
        zones = self.component_handler.get_areas_id()
        zones_table = {}
        elements = range(len(zones))

        for i in elements:
            for combin in combinations(elements, i + 1):
                keys, values = [], []
                for j in combin:
                    keys += [str(j + 1)]
                    values += [str(zones[j])]
                key = "zone" + "_".join(keys)
                if f"{{{key}}}" in self.text:
                    zones_table[key] = self.component_handler.merge_area(
                        values
                    ).areaName.values[0]

        zones_values = set(zones_table.values())
        if len(zones_values) != len(zones_table):
            self.handle_areaNameProblem(zones_table, zones, parent_function)

        self.text = self.text.format(**zones_table)

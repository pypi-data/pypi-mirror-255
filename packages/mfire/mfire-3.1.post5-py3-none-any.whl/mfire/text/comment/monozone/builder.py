from mfire.settings import get_logger
from mfire.text.base import BaseBuilder
from mfire.text.period_describer import PeriodDescriber
from mfire.utils.date import Period

# Logging
LOGGER = get_logger(name="text_builder.mod", bind="text_builder")


class PeriodBuilder(BaseBuilder):
    """Processes period tags in a comment.

    Inherits:
        BaseBuilder
    """

    def build_period(self, reduction: dict) -> None:
        """Populates the template with period elements.

        Targets tags of the form {Bi_period}, {Bi_start}, {Bi_stop}.

        Args:
            reduction (dict): Dictionary containing the information.
        """
        prod_date = reduction["production_datetime"]
        period_table = {}

        # Process each key-value pair in the reduction dictionary
        for k, v in reduction.items():
            # Check if the value is a dictionary with 'start' and 'stop' keys
            if isinstance(v, dict) and "start" in v and "stop" in v:
                # Get the period description, start description, and stop description
                period = PeriodDescriber(prod_date).describe(
                    Period(v["start"], v["stop"])
                )
                start = PeriodDescriber(prod_date).describe(Period(v["start"]))
                stop = PeriodDescriber(prod_date).describe(Period(v["stop"]))

                # Add the period elements to the period table
                period_table[k + "_period"] = period
                period_table[k + "_start"] = start
                period_table[k + "_stop"] = stop

        # Replace placeholders in the text template with period table values
        self.text = self._text.format(**period_table)

from mfire.settings import get_logger
from mfire.text.comment.monozone import PeriodBuilder
from mfire.text.comment.representative_builder import RepresentativeValueManager
from mfire.utils.string_utils import clean_french_text

# Logging
LOGGER = get_logger(name="text_monozone.mod", bind="text_monozone")


class Monozone(PeriodBuilder, RepresentativeValueManager):
    """Specific builder for handling "monozone" type components."""

    @staticmethod
    def compare_param(max_val: dict, param: dict) -> bool:
        """Compares representative values for cumulative values.

        If the values are equal, the comparison is based on the mountain value.

        Args:
            max_val (dict): The current maximum representative values.
            param (dict): The parameter information.

        Returns:
            bool: True if the value in max_val is the largest, False otherwise.
        """

        try:
            operator = param["plain"]["operator"].strict
            if operator(max_val["plain"]["value"], param["plain"]["value"]):
                return True
            if param["plain"]["value"] != max_val["plain"]["value"]:
                return False
        except KeyError:
            pass

        try:
            operator = param["mountain"]["operator"]
            return operator(
                max_val["mountain"]["value"],
                param["mountain"]["value"],
            )
        except KeyError:
            return True

    def process_rep_value(self, reduction):
        """Processes the representative values for the comment.

        For cumulative values, only the highest-level block is considered.

        Args:
            reduction (dict): The block reduction.
        """
        rep_value_table = {}
        for bloc, data in reduction.items():
            if isinstance(data, dict):
                data_dict = {
                    k: v
                    for k, v in data.items()
                    if k not in ["start", "stop", "centroid_value"]
                }

                if not data_dict.get("level"):
                    data_dict["level"] = -1
                if bool(data_dict) and data_dict["level"] != 0:
                    rep_value_table[f"{bloc}_val"] = data_dict

        if reduction["type"] in ["SNOW", "PRECIP", "PRECIP_SNOW"]:
            max_val = {}
            for bloc, data in rep_value_table.items():
                if data["level"] == reduction["risk_max"]:
                    for key, param in data.items():
                        if key in max_val and self.compare_param(max_val[key], param):
                            pass
                        elif key != "level":
                            max_val[key] = param
            if max_val:
                self.text += self.get_rep_value(max_val)[:-1]
        else:
            final_rep_value = {
                key: self.get_rep_value(
                    {k: v for k, v in value.items() if k != "level"}
                )[:-1]
                for key, value in rep_value_table.items()
                if len(value) > 1
            }
            self.text = self._text.format(**final_rep_value)

    def compute(self, reduction):
        """Generates the comment.

        Args:
            reduction (dict): The block reduction.
        """
        if reduction["template"] == "R.A.S.":
            return reduction["template"]

        self.build_period(reduction)
        self.process_rep_value(reduction)
        self.text = clean_french_text(self.text)

        name = reduction["compo_hazard"] + "_" + str(reduction["production_datetime"])
        for_log = {
            name.replace(" ", "_"): {
                k: reduction[k]
                for k in [
                    "level_maxi",
                    "risk_max",
                    "risk_min",
                    "reduced",
                    "centroid",
                    "template",
                    "production_datetime",
                ]
            }
        }

        LOGGER.debug(f"LOGINFO |{for_log}|")

        return self._text

from __future__ import annotations

from abc import ABC
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

from mfire.configuration.rules import CommonRules
from mfire.settings import TEMPLATES_FILENAMES, Settings, get_logger
from mfire.text.base import BaseBuilder
from mfire.text.comment.multizone import ComponentInterface
from mfire.text.template import Template, TemplateRetriever, read_template
from mfire.utils.string_utils import (
    capitalize,
    concatenate_string,
    get_synonym,
    split_accumulation_var_name,
)

# Logging
LOGGER = get_logger(
    name="text.representative_builder.mod", bind="text.representative_builder"
)


class RepresentativeValueClass(ABC, BaseBuilder):
    @staticmethod
    def get_builder_by_prefix(prefix: str) -> Optional[RepresentativeValueBuilder]:
        if prefix == "FF":
            return FFBuilder()
        if prefix == "RAF":
            return FFRafBuilder()
        if prefix == "T":
            return TemperatureBuilder()
        if prefix in ["PRECIP", "EAU"]:
            return PrecipBuilder()
        if prefix == "NEIPOT":
            return SnowBuilder()
        return None


class RepresentativeValueManager(RepresentativeValueClass):
    """
    This class enable to manage all text for representative values.
    It chooses which class needs to be used for each case.
    """

    # used to retrieve the base param name from its aggregated form
    rules: CommonRules = CommonRules()
    aggregation_rules: pd.DataFrame = rules.agg_param_df
    family_rules: pd.DataFrame = rules.family_param_df
    component_handler: Optional[ComponentInterface] = None

    def process_rep_value(self, reduction: dict):
        """
        The various representative values are processed. If a reduction is given,
        it means that we are in the monozone case

        Args:
            reduction (dict): Dictionary of reduction in monozone case

        Returns:
            [Optional[str]]: Processed text or None
        """
        value = self.get_rep_value(reduction)
        if value is not None:
            self._text += value

    def get_rep_value(self, reduction: dict) -> Optional[str]:
        """
        Get representative values. If a reduction is given, it means that we are in
        the monozone case

        Args:
            reduction (dict): Dictionary of reduction in monozone case

        Returns:
            [Optional[str]]: Processed text or None
        """
        if reduction:
            dict_value = reduction
        elif self.component_handler is not None:
            dict_value = self.component_handler.get_critical_value()
        else:
            return None

        altitudes = [
            v["mountain_altitude"]
            for v in dict_value.values()
            if "mountain_altitude" in v
        ]
        if len(altitudes) == len(dict_value) and len(set(altitudes)) == 1:
            # in the case of a Bertrand type component, we will handle all the
            # cumulative snow variables together
            return AltitudeBuilder().format("_", dict_value)

        # we don't build a phrase when in a case of a complex risk
        # (composition of atomic risks) except if the risks are of the same type
        # e.g.: if a risk is triggerd by either wind or snow => no description
        # but if a risk is either snow__1H or snow_24H => we build a description
        # if a risk is FF and FF_RAF => we also build a description
        are_values_homogenous = self.are_values_homogenous(dict_value)
        if not are_values_homogenous and len(dict_value) > 1:
            return ""

        # Otherwise for the moment we add a sentence for each of the variables present
        val_rep = ""
        if len(dict_value) == 1 or are_values_homogenous:
            for key, value in dict_value.items():
                prefix, _, _ = split_accumulation_var_name(key)
                value_builder = self.get_builder_by_prefix(prefix)
                if value_builder is not None:
                    formatted = value_builder.format(key, value)
                    if formatted is not None:
                        val_rep += f"{formatted} "
        return val_rep.rstrip()

    def are_values_homogenous(self, dict_params: dict) -> bool:
        """checks uf all the parameters represent the same phenomenon, but with
        different time aggregations. For instance:
        ["NEIPOT1__SOL", "NEIPOT6__SOL", "NEIPOT24__SOL"] returns True
        ["NEIPOT1__SOL", "PRECIP__SOL", "EAU1__SOL"] returns True since same family
        ["FF__HAUTEUR", "RAF__HAUTEUR"] returns True since same family
        ["NEIPOT1__SOL", "FF__HAUTEUR"] returns False since different families
        ["XXX__HAUTEUR"] returns False since XXX isn't a family

        Args:
            dict_params (dict): all the parameters that are triggered an alert

        Returns:
            bool: True if all the parameters are similar, False otherwise
        """
        family = None
        for param in dict_params.keys():
            # we search for the base name of the current param
            if param in self.aggregation_rules.index:
                base_param = self.aggregation_rules.loc[param]["param"]
            else:
                base_param, _, _ = split_accumulation_var_name(param)

            if base_param not in self.family_rules.index:
                return False

            # then we look for its family
            param_family = self.family_rules.loc[base_param]["family"]
            family = family or param_family

            # this param is different from the reference, no need to search further
            if param_family != family:
                return False

        return True


class RepresentativeValueBuilder(RepresentativeValueClass):
    """
    This class enable to speak about representative values
    """

    phenomenon: str = ""
    def_article: str = ""
    indef_article: str = ""
    around_word: str = "aux alentours de"
    feminine: bool = False
    plural: bool = False
    multizone_template: str = "rep_val"
    template_retriever: Optional[TemplateRetriever] = None

    @staticmethod
    def accumulated_hours(var_name: str) -> str:
        """
        Gets the number of hours over which the var_name is accumulated

        Args:
            var_name (str): Name of the var_name

        Returns:
            [str]: Number of hours over which the var_name is accumulated
        """
        _, accum, _ = split_accumulation_var_name(var_name)

        if not accum:
            return ""

        accum_text = f"{accum} heure"
        if int(accum) > 1:
            accum_text += "s"

        return accum_text

    @property
    def around(self) -> str:
        """
        Returns a synonym of the around
        """
        return get_synonym(self.around_word)

    @staticmethod
    def units(unit: Optional[str]) -> str:
        """
        Get the unity. If None then it returns an empty string
        """
        return unit or ""

    @staticmethod
    def round(x: Optional[float], **_kwargs) -> Optional[str]:
        """
        Make a rounding of the value

        Args:
            x (Optional[float]): Value to round

        Returns:
            [Optional[str]]: String of the rounded value or None if not possible
        """
        return str(x) if x is not None and abs(x) > 1e-6 else None

    @staticmethod
    def replace_critical(dict_in: Dict) -> Tuple[Optional[float], Optional[float]]:
        operator, value, next_critical, threshold = (
            dict_in.get("operator"),
            dict_in.get("value"),
            dict_in.get("next_critical"),
            dict_in.get("threshold"),
        )
        if value is None or operator is None:
            return None, None
        if next_critical is not None and operator(value, next_critical):
            rep_value = next_critical + np.sign(next_critical - value)
            local = value
        else:
            rep_value = value
            local = (
                threshold
                if dict_in.get("occurrence_event") and operator(threshold, value)
                else None
            )  # handling of too low/high values compared with the threshold (#38212)
        return rep_value, local

    def definite_var_name(self, var_name: str) -> str:
        """
        Returns the definite var_name name

        Args:
            var_name (str): Name of the var_name
        """
        return f"{self.def_article} {self.phenomenon}"

    def indefinite_var_name(self, var_name: str) -> str:
        """
        Returns the indefinite var_name name

        Args:
            var_name (str): Name of the var_name
        """
        return f"{self.indef_article} {self.phenomenon}"

    def template(self, key: Optional[str]) -> Template:
        """
        Returns the template associated to the var_name name and sentence type

        Args:
            key (Optional[str]): Key of the template

        Returns:
            [Dict]: Dictionary of all information of the phenomenon
        """
        if self.template_retriever is None:
            self.template_retriever = read_template(
                TEMPLATES_FILENAMES[Settings().language]["multizone"][
                    self.multizone_template
                ]
            )
        default = f"Echec dans la récupération du template (key={key}) (error COM-001)."
        sentence = self.template_retriever.get(key=key, default=default)
        return Template(sentence)

    def get_sentence_and_format_table(
        self, var_name: str, dict_in: Dict
    ) -> Optional[Tuple[str, Dict]]:
        """
        Returns the sentence and format table associated to the var_name and information
        or None if it's not possible

        Args:
            var_name (str): Variable name
            dict_in (Dict): Information of the var_name

        Returns:
            [Optional[Tuple[str,Dict]]]: Tuple consisted of the sentence and the
                                        information or None if not possible
        """
        local_plain, rep_plain, key = None, None, None

        format_table = {
            "phenomenon": self.phenomenon,
            "definite_var_name": self.definite_var_name(var_name),
            "indefinite_var_name": self.indefinite_var_name(var_name),
            "feminine": "e" if self.feminine else "",
            "plural": "s" if self.plural else "",
            "around": self.around,
        }

        if "plain" in dict_in:
            plain_dict = dict_in["plain"]
            operator = plain_dict.get("operator")
            rep_value, local = self.replace_critical(plain_dict)
            rep_plain = self.round(
                rep_value, operator=operator, around=format_table["around"]
            )
            if rep_plain is None:
                return None

            format_table["value"] = f"{rep_plain} {self.units(plain_dict['units'])}"

            local_plain = self.round(
                local, operator=operator, around=format_table["around"]
            )
            if local_plain is not None and local_plain != rep_plain:
                key = "local_plain"
                format_table[
                    "local_value"
                ] = f"{local_plain} {self.units(plain_dict['units'])}"
            else:
                key = "plain"

        if "mountain" in dict_in:
            mountain_dict = dict_in["mountain"]
            operator = mountain_dict.get("operator")
            rep_value, local = self.replace_critical(mountain_dict)
            rep_mountain = self.round(
                rep_value, operator=operator, around=format_table["around"]
            )
            if rep_mountain is None:
                return None

            if rep_plain != rep_mountain:
                key = f"{key}_" if key is not None else ""

                format_table["hauteur"] = "sur les hauteurs"
                format_table["altitude"] = dict_in.get("mountain_altitude")
                format_table[
                    "mountain_value"
                ] = f"{rep_mountain} {self.units(mountain_dict['units'])}"

                local_mountain = self.round(
                    local, operator=operator, around=format_table["around"]
                )
                if local_mountain is not None and local_mountain != rep_mountain:
                    key += "local_mountain"
                    format_table["local_mountain_value"] = (
                        f"{local_mountain} "
                        f"{self.units(dict_in['mountain']['units'])}"
                    )
                else:
                    key += "mountain"
        return (self.template(key), format_table) if key is not None else None

    def format(self, var_name: str, dict_in: dict) -> Optional[str]:
        """
        Returns the formatted sentence associated to the variable and the given
        information

        Args:
            var_name (str): Variable name
            dict_in (Dict): Information of the var_name

        Returns:
            [Optional[str]]: Formatted string or None if not possible
        """
        sentence_and_format_table = self.get_sentence_and_format_table(
            var_name, dict_in
        )
        if sentence_and_format_table is None:
            return None

        sentence, format_table = sentence_and_format_table
        rep_value = format_table.get("mountain_value") or format_table["value"]

        if rep_value.startswith("au"):
            format_table["around"] = "d'"
            sentence = sentence.replace("{around} ", "{around}")
        return capitalize(sentence.format(**format_table))

    def short_description(
        self, var_name: str, dict_in: dict, only_values: bool
    ) -> Optional[str]:
        # calcul de la valeur representative et local (si existe)
        rep_value, local_value = self.replace_critical(dict_in)
        rep_value = self.round(
            rep_value,
            operator=dict_in["operator"],
            around=self.around,
        )

        if rep_value is None:
            return None

        local_value = self.round(
            local_value,
            operator=dict_in["operator"],
            around=self.around,
        )
        if local_value is not None and local_value != rep_value:
            local_desc = f" (localement {local_value} {self.units(dict_in['units'])})"
        else:
            local_desc = ""

        # description textuelle de la valeur
        value_desc = f"{rep_value} {self.units(dict_in['units'])}{local_desc}"

        # description textuelle de l'accumulation
        _, accum, _ = split_accumulation_var_name(var_name=var_name)
        if accum > 0:
            value_desc = f"{value_desc} en {accum} h"

        return (
            value_desc
            if only_values
            else f"{self.indef_article} {self.phenomenon} de {value_desc}"
        )


class FFBuilder(RepresentativeValueBuilder):
    """
    Classe spécifique pour le vent
    """

    phenomenon = "vent moyen"
    def_article = "le"
    indef_article = "un"
    intro_var = "le vent moyen"
    var_d = "un vent moyen"
    feminine = False
    plural = False

    @staticmethod
    def round(x: Optional[float], **kwargs) -> Optional[str]:
        """
        Rounds values to the nearest interval of 5.
        Examples:
            Input --> Output
             7.5   -->  5 à 10
             12.5   -->  10 à 15

        Args:
            x (float): Value to round

        Returns:
            [Optional[str]]: Rounded value or None if not possible
        """
        if super(FFBuilder, FFBuilder).round(x, **kwargs) is None:
            return None
        start = (int(x / 5)) * 5
        stop = start + 5
        return f"{start} à {stop}"


class TemperatureBuilder(RepresentativeValueBuilder):
    """
    Classe spécifique pour la température
    """

    phenomenon = "température"
    def_article = "la"
    indef_article = "une"
    feminine = True
    plural = False

    @staticmethod
    def round(x: Optional[float], operator: str = "<", **kwargs) -> Optional[str]:
        """
        Rounds down or up as appropriate.
        Examples:
            Input --> Output
             7.5 + <=  -->  7
             7.5 + >= -->  8

        Args:
            x (float): Value to round

        Returns:
            [Optional[str]]: Rounded value or None if not possible
        """
        if x is None:
            return None
        if operator in ("<", "<=", "inf", "infegal"):
            return str(int(np.floor(x)))
        return str(int(np.ceil(x)))


class FFRafBuilder(RepresentativeValueBuilder):
    """
    Classe spécifique pour le vent
    """

    phenomenon: str = "rafales"
    def_article: str = "les"
    indef_article: str = "des"
    around_word: str = "de l'ordre de"
    feminine = True
    plural = True

    multizone_template: str = "rep_val_FFRaf"

    @staticmethod
    def round(x: Optional[float], **kwargs) -> Optional[str]:
        """
        Rounds values to the nearest interval of 10.
        Examples:
            Input                            --> Output
             7.5, around=None                -->  5 à 10
             7.5, around="comprises entre"   -->  5 et 10

        Args:
            x (float): Value to round

        Returns:
            [Optional[str]]: Rounded value or None if not possible
        """
        if super(FFRafBuilder, FFRafBuilder).round(x, **kwargs) is None:
            return None
        start = (int(x / 10)) * 10
        stop = start + 10
        to = "et" if kwargs.get("around") == "comprises entre" else "à"
        return f"{start} {to} {stop}"


class SnowBuilder(RepresentativeValueBuilder):
    """
    Classe spécifique pour la neige
    """

    phenomenon = "potentiel de neige"
    def_article = "le"
    indef_article = "un"
    feminine = False
    plural = False

    def definite_var_name(self, variable: str) -> str:
        """
        Returns the definite var_name
        """
        intro = super().definite_var_name(variable)
        return f"{intro} sur {self.accumulated_hours(variable)}"

    def indefinite_var_name(self, variable: str) -> str:
        """
        Returns the indefinite var_name
        """
        intro = super().indefinite_var_name(variable)
        return f"{intro} sur {self.accumulated_hours(variable)}"

    @staticmethod
    def round(x: Optional[float], **kwargs) -> Optional[str]:
        """
        Foncion pour arrondir les valeurs à l'intervalle de  5 le plus proche.
        Exemples:
            Input --> Output
             42   -->  40 à 45
             39   -->  35 à 40
        """
        if super(SnowBuilder, SnowBuilder).round(x, **kwargs) is None:
            return None
        if x < 1:
            return "0 à 1"
        if x < 3:
            return "1 à 3"
        if x < 5:
            return "3 à 5"
        if x < 7:
            return "5 à 7"
        if x < 10:
            return "7 à 10"
        if x < 15:
            return "10 à 15"
        if x < 20:
            return "15 à 20"
        start = int(x / 10) * 10
        stop = start + 10
        return f"{start} à {stop}"


class PrecipBuilder(RepresentativeValueBuilder):
    """
    Classe spécifique pour les précipitations
    """

    phenomenon = "cumul pluie"
    feminine = False
    plural = False

    def definite_var_name(self, var_name: str) -> str:
        """
        Returns the definite var_name
        """
        prefix, _, _ = split_accumulation_var_name(var_name)
        if prefix == "PRECIP":
            return f"le cumul de précipitation sur {self.accumulated_hours(var_name)}"
        if prefix == "EAU":
            return f"le cumul de pluie sur {self.accumulated_hours(var_name)}"
        LOGGER.error(f"Prefix unknown. Get {prefix}")
        return ""

    def indefinite_var_name(self, var_name: str) -> str:
        """
        Returns the indefinite var_name
        """
        prefix, _, _ = split_accumulation_var_name(var_name)
        if prefix == "PRECIP":
            return f"un cumul de précipitation sur {self.accumulated_hours(var_name)}"
        if prefix == "EAU":
            return f"un cumul de pluie sur {self.accumulated_hours(var_name)}"
        LOGGER.error(f"Prefix unknown. Get {prefix}")
        return ""

    @staticmethod
    def round(x: Optional[float], **kwargs) -> Optional[str]:
        """
        Foncion pour arrondir les valeurs à l'intervalle de  5 le plus proche.
        Exemples:
            Input --> Output
             42   -->  40 à 45
             39   -->  35 à 40
        """
        if super(PrecipBuilder, PrecipBuilder).round(x, **kwargs) is None:
            return None
        if x < 3:
            return "au maximum 3"
        if x < 7:
            return "3 à 7"
        if x < 10:
            return "7 à 10"
        if x < 15:
            return "10 à 15"
        if x < 20:
            return "15 à 20"
        if x < 25:
            return "20 à 25"
        if x < 30:
            return "25 à 30"
        if x < 40:
            return "30 à 40"
        if x < 50:
            return "40 à 50"
        if x < 60:
            return "50 à 60"
        if x < 80:
            return "60 à 80"
        if x < 100:
            return "80 à 100"
        start = (int(x / 50)) * 50
        stop = (int(x / 50)) * 50 + 50
        return f"{start} à {stop}"


class AltitudeBuilder(SnowBuilder):
    """
    Classe spécifique pour la neige
    """

    feminine = False

    def get_sentence_and_format_table(
        self, var_name: str, dict_in: dict
    ) -> Optional[Tuple[str, Dict]]:
        """
        Returns the sentence and format table associated to the var_name and information
        or None if it's not possible

        Args:
            var_name (str): Variable name
            dict_in (Dict): Information of the var_name

        Returns:
            [Optional[Tuple[str,Dict]]]: Tuple consisted of the sentence and the
                                        information or None if not possible
        """
        format_table = {
            "phenomenon": self.phenomenon,
            "around": self.around,
            "altitude": next(
                (
                    var_dict.get("mountain_altitude")
                    for var_dict in dict_in.values()
                    if "mountain_altitude" in var_dict
                ),
                0,
            ),
            "feminine": "e" if self.feminine else "",
            "plural": "s" if self.plural else "",
        }

        sorted_vars = sorted(
            [(v, *split_accumulation_var_name(v)) for v in dict_in], key=lambda x: x[2]
        )
        var_prefixes = set(v[1] for v in sorted_vars)

        # s'il n'y a qu'un type de var_name, on enumera juste les valeurs
        only_values = len(var_prefixes) == 1
        value_builder = None

        for stage in ("plain", "mountain"):
            var_desc_list = []
            for var, prefix, _, _ in sorted_vars:
                stage_var_dict = dict_in[var].get(stage)
                if stage_var_dict is None:
                    continue
                value_builder = self.get_builder_by_prefix(prefix)
                if value_builder is not None:
                    var_desc = value_builder.short_description(
                        var,
                        stage_var_dict,
                        only_values,
                    )
                    if var_desc is not None:
                        var_desc_list.append(var_desc)

            if value_builder is not None and value_builder.phenomenon is not None:
                format_table["phenomenon"] = value_builder.phenomenon
                format_table["feminine"] = "e" if value_builder.feminine else ""
                format_table["plural"] = "s" if value_builder.plural else ""

            key = "value" if stage == "plain" else "mountain_value"
            if len(var_desc_list) == 1:
                format_table[key] = var_desc_list[0]
            elif len(var_desc_list) > 1:
                format_table[key] = concatenate_string(var_desc_list)

        sentence = ""
        if "value" in format_table:
            sentence += (
                "Surveillance client sous {altitude} m : {phenomenon} maximal{feminine}"
                "{plural} = {value}. "
            )
        if "mountain_value" in format_table:
            sentence += (
                "Surveillance client au-dessus de {altitude} m : {phenomenon} maximal"
                "{feminine}{plural} = {mountain_value}."
            )

        return (sentence.rstrip(), format_table) if sentence != "" else None

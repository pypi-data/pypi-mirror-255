import re

from mfire.settings import LANGUAGE, TEMPLATES_FILENAMES
from mfire.text.base import BaseBuilder
from mfire.text.common import SynonymeBuilder, TemplateBuilder, ZoneBuilder
from mfire.text.temperature import TemperatureSelector
from mfire.text.template import read_template

TEMPE_TPL_RETRIEVER = read_template(
    TEMPLATES_FILENAMES["fr"]["synthesis"]["temperature"]
)


class TemperatureBuilder(
    TemplateBuilder,
    SynonymeBuilder,
    ZoneBuilder,
    BaseBuilder,
):
    """Builder spécifique pour gérer les textes de synthèse pour la température

    Args:
        Objet qui est capable de trouver et de fournir un modèle
        correspondant à self.reducer.

    Inheritance:
        BaseBuilder
        SynonymeBuilder
        ZoneBuilder
        PeriodBuilder
    """

    # pattern used to fix intervals with only one value
    pattern = re.compile(r" ([-]{0,1}\d+) " + LANGUAGE.a_grave + r" ([-]{0,1}\d+)°C")

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text

    @staticmethod
    def fix_single_value_intervals(text) -> str:
        """removes duplicate temperature for intervals with a single value
        e.g: "12 à 12° dans le Vercors" => "12° dans le Vercors"

        Args:
            text (str): the description text to be fixed

        Returns:
            str: the fixed description text
        """

        for match in TemperatureBuilder.pattern.finditer(text):
            interval_text = match.group(0)
            t1 = match.group(1)
            t2 = match.group(2)
            if t1 == t2:
                text = text.replace(interval_text, f" {t2}°C")

        return text

    def prettify_altitude_intervals(self):
        pass

    def to_upper(self):
        """Set the first letter of the sentence to upper case"""
        self.text = self.text[0].upper() + self._text[1:]

    def post_process(self):
        """Cleans up the generated text to make it more humanlike"""

        self.text = self.fix_single_value_intervals(self.text)
        self.prettify_altitude_intervals()
        self.to_upper()

    def compute(self, reduction: dict) -> None:
        self.reset()
        self.reduction = reduction
        selector = TemperatureSelector()
        key = self.find_template_key(selector)
        self.retrieve_template(key, TEMPE_TPL_RETRIEVER)
        self.handle_comment(reduction)
        self.build_zone()
        self.find_synonyme()
        self.post_process()

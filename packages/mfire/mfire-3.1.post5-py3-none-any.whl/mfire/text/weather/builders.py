from mfire.settings import TEMPLATES_FILENAMES, get_logger
from mfire.text.common import TemplateBuilder
from mfire.text.template import read_template
from mfire.text.weather import WeatherSelector

# Logging
LOGGER = get_logger(name="weather_builder.mod", bind="weather_builder")

TEMPE_TPL_RETRIEVER = read_template(TEMPLATES_FILENAMES["fr"]["synthesis"]["weather"])


class WeatherBuilder(TemplateBuilder):
    """Builder spécifique pour gérer les textes de synthèse pour la température

    Args:
        Objet qui est capable de trouver et de fournir un modèle
        correspondant à self.reducer.
    """

    template_name = "weather"
    selector_class = WeatherSelector

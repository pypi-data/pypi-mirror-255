"""
Choisi le type de type de texte de synthèse en fonction du paramètre (weather)
"""

from mfire.composite import WeatherComposite
from mfire.settings import get_logger
from mfire.text.temperature import TemperatureDirector
from mfire.text.weather import WeatherDirector
from mfire.text.wind import WindDirector

# Logging
LOGGER = get_logger(name="text_director_factory.mod", bind="text_director_factory")


class DirectorFactory:

    MAPPING: dict = {
        "tempe": TemperatureDirector(),
        "wind": WindDirector(),
        "weather": WeatherDirector(),
    }

    @classmethod
    def compute(cls, geo_id: str, weather: WeatherComposite):

        try:
            director = cls.MAPPING[weather.id]
        except KeyError:
            raise KeyError(
                f"No text Director found for the given Weather '{weather.id}'"
            )

        return director.compute(geo_id=geo_id, composite=weather)

"""
Module permettant de gérer la génération de textes de synthèses.
C'est dans ce module qu'on va décider vers quel module
de génération de texte de synthèse on va s'orienter.
"""

from mfire.text.base import BaseDirector
from mfire.text.temperature import TemperatureBuilder, TemperatureReducer


class TemperatureDirector(BaseDirector):
    """Module permettant de gérer la génération de textes de synthèse."""

    reducer: TemperatureReducer = TemperatureReducer()
    builder: TemperatureBuilder = TemperatureBuilder()

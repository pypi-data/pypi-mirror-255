"""
Module permettant de gérer la génération de textes de synthèses.
C'est dans ce module qu'on va décider vers quel module
de génération de texte de synthèse on va s'orienter.
"""

from mfire.composite import WeatherComposite
from mfire.settings import get_logger
from mfire.text.base import BaseBuilder, BaseReducer

# Logging
LOGGER = get_logger(name="base_director.mod", bind="base_director")


class BaseDirector:
    """Module permettant de gérer la génération de textes de synthèse."""

    reducer: BaseReducer = BaseReducer()
    builder: BaseBuilder = BaseBuilder()

    def compute(self, geo_id: str, composite: WeatherComposite) -> str:
        """
        Permet de récupérer le texte de synthèse

        Args:
            composite (TextComponentComposite) : composant à traiter

        Returns:
            str: texte de synthèse
        """

        # si il n'y a pas de condition on fait un texte,
        # si il y en a une on vérifie qu'elle est vérifiée
        if composite.condition is None or composite.check_condition:
            reduction = self.reducer.compute(geo_id=geo_id, composite=composite)

            self.builder.compute(reduction)
            return self.builder.text

        return ""

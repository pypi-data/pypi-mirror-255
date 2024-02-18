from abc import ABC, abstractmethod

from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="base_selector.mod", bind="base_selector")


class BaseSelector(ABC):
    """BaseSelector qui doit renvoyer une clé de template"""

    @abstractmethod
    def compute(self, reduction: dict) -> str:
        """génération du dictionnaire de choix, recherche dans la matrice
        du texte de synthèse pour déterminer la clé du template
        en fonction du paramètre
        """

from typing import Optional

import mfire.utils.mfxarray as xr
from mfire.composite import BaseComposite
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="base_reducer.mod", bind="base_reducer")


class BaseReducer:
    """Classe de base pour implémenter un reducer.
    Il adopte le design pattern du constructeur:
    - il existe un produit "summary" à construire (ici un dictionnaire)
    - une méthode "reset" qui permet de recommencer le processus de construction
    - un ensemble de méthode qui permettent d'ajouter des caractéristiques au "summary"
    - une méthode "compute" qui exécute l'ensemble des étapes et renvoie le "summary"

    '/!\' Dans les classes héritant de BaseReducer,
    il est impératif de détailler au niveau de cette docstring principale
    le schéma du dictionnaire de résumé issu de la méthode "compute".
    """

    data: Optional[xr.DataArray] = None
    geo_id: Optional[str] = None
    composite: Optional[BaseComposite] = None

    def __init__(self) -> None:
        self.data = None
        self.summary: dict = {}
        self.reset()

    def reset(self) -> None:
        """Méthode permettant de remettre à zéros le processus de construction
        du summary
        """
        self.data = None
        self.summary: dict = {}

    def compute(self, geo_id: str, composite: BaseComposite) -> dict:
        """Méthode permettant d'exécuter toutes les étapes de construction

        Args:
            composite (Composite): Composant sur lequels on se base pour produire le
            texte
        Returns:
            dict: Dictionnaire résumant les infos contenues dans le composite
        """
        self.reset()
        self.geo_id = geo_id
        self.composite = composite
        self.data = composite.compute(geo_id=geo_id, force=True)

        return self.summary

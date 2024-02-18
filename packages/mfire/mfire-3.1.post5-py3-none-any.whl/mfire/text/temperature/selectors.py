from mfire.text.base import BaseSelector


class TemperatureSelector(BaseSelector):
    """TemperatureSelector spécifique pour la temperature"""

    def compute(self, reduction: dict) -> str:
        """génération du dictionnaire de choix, recherche dans la matrice
        du texte de synthèse pour le température pour déterminer la clé du template
        en fonction du paramètre
        """

        # First iteration, only manages ranges of temperatures.
        # If one description only has a range of 1°C, its template will
        # give us something wonky,like "from 13°C to 13°C" :(
        # On the plus side, the code is really short :D
        tn = reduction["general"]["tempe"]["mini"]
        tx = reduction["general"]["tempe"]["maxi"]

        key = f"P1_Z0_{len(tn)}_MIN_{len(tx)}_MAX"

        return key

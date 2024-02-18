from __future__ import annotations

from mfire.settings import get_logger
from mfire.text.base import BaseBuilder

# Logging
LOGGER = get_logger(name="common_builder.mod", bind="common_builder")


class SynonymeBuilder(BaseBuilder):
    """SynonymeBuilder qui doit construire les synonyme du texte de synthèse"""

    def find_synonyme(self):
        pass

    def compute(self):

        self.find_synonyme()


class ZoneBuilder(BaseBuilder):
    """ZoneBuilder qui doit construire les zones du texte de synthèse"""

    def build_zone(self):
        pass

    def compute(self):

        self.build_zone()

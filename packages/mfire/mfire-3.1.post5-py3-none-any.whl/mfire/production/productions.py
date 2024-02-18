""" Gestion du fichier de sortie via l'objet OutputProduction
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, validator

from mfire.production.components import CDPComponents
from mfire.settings import get_logger
from mfire.utils import MD5, JsonFile
from mfire.utils.date import Datetime

LOGGER = get_logger(name="output.production.mod", bind="production.base")


class CDPProduction(BaseModel):
    """
    A CDP production.

    Attributes:
        production_id: The production ID.
        production_name: The production name.
        customer_id: The customer ID (optional).
        customer_name: The customer name (optional).
        date_bulletin: The bulletin date.
        date_production: The production date.
        date_configuration: The configuration date.
        components: The CDP components.
    """

    ProductionId: str
    ProductionName: str
    CustomerId: Optional[str]
    CustomerName: Optional[str]
    DateBulletin: Datetime
    DateProduction: Datetime
    DateConfiguration: Datetime
    Components: CDPComponents

    @validator("DateBulletin", "DateProduction", "DateConfiguration", pre=True)
    def init_dates(cls, v: str) -> Datetime:
        """
        Validates the dates and converts them to `Datetime` objects.

        Args:
            v: The date string.

        Returns:
            Datetime: The `Datetime` object.
        """
        return Datetime(v)

    @validator("CustomerId", "CustomerName", always=True)
    def init_customer(cls, v: str) -> str:
        """
        Validates the customer ID and name, and returns "unknown" if they are None.

        Args:
            v: The customer ID or name.

        Returns:
            str: The customer ID or name, or "unknown" if it is None.
        """
        return v or "unknown"

    @property
    def hash(self) -> str:
        """Hash of the object

        Returns:
            str: hash
        """
        return MD5(obj=self.dict()).hash

    def dump(self, dump_dir: Path) -> Optional[Path]:
        """
        Dumps self to a JSON file.

        Args:
            dump_dir (Path): Working directory where to dump
        """
        filename = dump_dir / f"prom_{self.ProductionId}_{self.hash}.json"
        filename.parent.mkdir(parents=True, exist_ok=True)
        JsonFile(filename).dump(self.dict(exclude_none=True))
        if filename.is_file():
            return filename

        LOGGER.error(f"Failed to dump {filename}.")
        return None

    @classmethod
    def concat(cls, productions: List[CDPProduction]) -> Optional[CDPProduction]:
        """
        Concatenates a list of CDP productions.

        Args:
            productions: The list of CDP productions to concatenate.

        Returns:
            The concatenated CDP production, or `None` if the list is empty.
        """
        if len(productions) == 0:
            return None
        production = productions.pop(0)
        for other_production in productions:
            production += other_production
        return production

    def __add__(self, other: CDPProduction) -> CDPProduction:
        return CDPProduction(
            ProductionId=self.ProductionId,
            ProductionName=self.ProductionName,
            CustomerId=self.CustomerId,
            CustomerName=self.CustomerName,
            DateBulletin=self.DateBulletin,
            DateProduction=self.DateProduction,
            DateConfiguration=self.DateConfiguration,
            Components=self.Components + other.Components,
        )

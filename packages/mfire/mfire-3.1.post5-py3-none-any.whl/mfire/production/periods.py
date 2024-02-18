from __future__ import annotations

from pydantic import BaseModel, validator

from mfire.composite.periods import Period
from mfire.utils.date import Datetime


class CDPPeriod(BaseModel):
    """A class for creating a Period object containing the configuration of the
    periods of the Promethee production task.

    Args:
        baseModel (BaseModel): A Pydantic model.

    Returns:
        baseModel (BaseModel): A Period object.
    """

    PeriodId: str
    PeriodName: str
    DateDebutPeriode: Datetime
    DateFinPeriode: Datetime

    @validator("DateDebutPeriode", "DateFinPeriode", pre=True)
    def init_dates(cls, v: str) -> Datetime:
        """A validator for the start and end dates.

        Args:
            v (str): The start or end date as a string.

        Returns:
            datetime: The start or end date as a datetime object.
        """
        return Datetime(v)

    @classmethod
    def from_composite(cls, period: Period) -> CDPPeriod:
        """A class method for transforming a composite period into an
        actual Output CDP Model period.

        Args:
            period (Period): A Composite Period object.

        Returns:
            CDPPeriod: An Output Model.
        """
        return CDPPeriod(
            PeriodId=period.id,
            PeriodName=period.name or f"Du {period.start} au {period.stop}",
            DateDebutPeriode=period.start,
            DateFinPeriode=period.stop,
        )

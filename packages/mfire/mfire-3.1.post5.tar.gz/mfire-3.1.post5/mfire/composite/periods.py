from typing import Any, List, Optional

from pydantic import BaseModel, validator

from mfire.utils.date import Datetime


class Period(BaseModel):
    """
    Represents a Period object containing the configuration of production task periods
    in Promethee.

    Args:
        BaseModel: Pydantic base model.

    Returns:
        BaseModel: Period object.
    """

    id: str
    name: Optional[str] = None
    start: Datetime
    stop: Datetime

    @validator("start", "stop", pre=True)
    def init_boundaries(cls, v: str) -> Datetime:
        """
        Validator function to initialize the start and stop boundaries of the period.

        Args:
            v: Value of the start or stop boundary.

        Returns:
            Datetime: Validated and initialized boundary value.
        """
        return Datetime(v)


class PeriodCollection(BaseModel):
    """
    Represents a PeriodCollection object containing a list of periods for the
    production task in Promethee.

    Args:
        BaseModel: Pydantic base model.

    Returns:
        List[BaseModel]: List of Period objects.
    """

    periods: List[Period]

    def __iter__(self):
        """Iterate over the periods."""
        return iter(self.periods)

    def __len__(self):
        """Return the length of periods."""
        return len(self.periods)

    def __getitem__(self, idx: str) -> Period:
        """Get the period at the given index."""
        try:
            return next(period for period in self.periods if period.id == idx)
        except StopIteration as excpt:
            raise KeyError(f"'{idx}'") from excpt

    def get(self, index: str, default: Any = None) -> Period:
        """
        Get the period at the given index with a default value in case it is not found.

        Args:
            index: Index of the period.
            default: Default value to return if the period is not found.

        Returns:
            Period: The period object if found, otherwise the default value.
        """
        try:
            return self[index]
        except KeyError:
            return default

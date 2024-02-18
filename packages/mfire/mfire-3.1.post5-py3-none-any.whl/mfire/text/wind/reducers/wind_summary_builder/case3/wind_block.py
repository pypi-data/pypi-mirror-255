from __future__ import annotations

from typing import Optional

from mfire.settings import get_logger
from mfire.text.wind.exceptions import WindSynthesisError
from mfire.text.wind.reducers.wind_summary_builder.helpers import (
    SummaryKeysMixin,
    WindPeriodMixin,
    WindType,
)
from mfire.text.wind.reducers.wind_summary_builder.wind_direction import (
    WindDirectionPeriod,
)
from mfire.text.wind.reducers.wind_summary_builder.wind_force import (
    WindForcePeriod,
)
from mfire.utils.date import Datetime

LOGGER = get_logger(name="wind_block.mod", bind="wind_block")


class WindBlock(SummaryKeysMixin, WindPeriodMixin):
    """WindBlock class."""

    def __init__(
        self,
        begin_time: Datetime,
        end_time: Datetime,
        wind_type: WindType,
        flag: bool = False,
        wf_periods: Optional[list[WindForcePeriod]] = None,
        wd_periods: Optional[list[WindDirectionPeriod]] = None,
    ):
        """Initialize a WindBlock instance.

        A WindBlock is flagged (meaning _flag attribute is turn to True) if it has the
        type 3 and if it lasts more than 3 hours, or it has the maximum WindForce
        between all WindBlocks. A type 2 WindBlock can not be flagged: in this case, a
        ValueError is raised.
        """
        self._wind_type: WindType = wind_type
        self._flag: bool = flag
        self._wf_periods: list[WindForcePeriod] = []
        self._wd_periods: list[WindDirectionPeriod] = []
        super().__init__(begin_time, end_time)

        if wf_periods:
            self.wf_periods = wf_periods

        if wd_periods:
            self.wd_periods = wd_periods

    @property
    def wf_periods(self) -> list[WindForcePeriod]:
        """Get the wind force periods."""
        return self._wf_periods

    @wf_periods.setter
    def wf_periods(self, wf_periods: Optional[list[WindForcePeriod]]) -> None:
        """Set the wind force periods."""
        if not wf_periods:
            wf_periods = []
        self._check_input_periods(wf_periods, WindForcePeriod)
        self._wf_periods = wf_periods

    @property
    def wd_periods(self) -> list[WindDirectionPeriod]:
        """Get the wind direction periods."""
        return self._wd_periods

    @wd_periods.setter
    def wd_periods(self, wd_periods: Optional[list[WindDirectionPeriod]]) -> None:
        """Set the wind direction periods."""
        if not wd_periods:
            wd_periods = []
        self._check_input_periods(wd_periods, WindDirectionPeriod)
        self._wd_periods = wd_periods

    @property
    def wf_periods_cnt(self) -> int:
        """Get the counter of the wind force periods."""
        return len(self._wf_periods)

    @property
    def wd_periods_cnt(self) -> int:
        """Get the counter of the wind direction periods."""
        return len(self._wd_periods)

    @property
    def wind_type(self) -> WindType:
        """Get the WindBlock wind_type."""
        return self._wind_type

    @wind_type.setter
    def wind_type(self, wind_type: WindType) -> None:
        """Set the WindBlock wind_type."""
        self._wind_type = wind_type

    @property
    def flag(self) -> bool:
        """Get the WindBlock flag."""
        return self._flag

    @flag.setter
    def flag(self, flag: bool) -> None:
        """Set the WindBlock flag."""
        if self.wind_type == WindType.TYPE_2 and flag is True:
            raise ValueError("A WindBlock with type 2 can not be flagged")
        self._flag = flag

    def _check_input_periods(
        self, periods: list[WindForcePeriod] | list[WindDirectionPeriod], item_class
    ) -> None:
        """Check if input periods."""
        periods_len: int = len(periods)

        if periods_len == 0:
            return

        for period in periods:
            if isinstance(period, item_class) is False:
                raise TypeError(
                    f"Bad period type '{type(period)}' found in '{item_class}' list: "
                    f"{period}"
                )

        if periods[0].begin_time < self.begin_time:
            raise WindSynthesisError(
                f"begin_time of the 1st period '{periods[0].begin_time}' is < "
                f"block begin_time '{self.begin_time}' !"
            )

        if periods[-1].end_time > self.end_time:
            raise WindSynthesisError(
                f"end_time of the last period'{periods[0].begin_time}' is > "
                f"block end_time '{self.begin_time}' !"
            )

        if periods_len == 1:
            return

        period_cur: WindForcePeriod = periods[0]

        for i in range(1, periods_len):

            period_next: WindForcePeriod = periods[i]

            if period_cur.end_time > period_next.begin_time:
                raise WindSynthesisError(
                    f"Temporally unordered periods found: {period_cur} does not precede"
                    f"{period_next} !"
                )

            period_cur = period_next

    def merge(self, other: WindBlock) -> WindBlock:
        """Merge the wind block with another one.

        The begin_time, the wind_type and the flag of the output are those of self.
        """

        if (
            other.begin_time < self.end_time < other.end_time
            or self.begin_time < other.end_time < self.end_time
        ):
            raise WindSynthesisError(f"Cannot merge these 2 blocks:\n{self}\n{other} !")

        blocks: list[WindBlock] = [
            min([self, other], key=lambda b: b.begin_time),
            max([self, other], key=lambda b: b.begin_time),
        ]

        # Merge periods
        wf_periods: list[WindForcePeriod] = []
        wd_periods: list[WindDirectionPeriod] = []

        if self.flag is True:
            # Keep both wf_periods and wd_periods of each blocks
            for block in blocks:
                if block.wind_type == WindType.TYPE_3:
                    wf_periods.extend(block.wf_periods)
                    wd_periods.extend(block.wd_periods)
        else:
            # Keep only wd_periods of each blocks
            for block in blocks:
                if block.wind_type in [WindType.TYPE_2, WindType.TYPE_3]:
                    wd_periods.extend(block.wd_periods)

        wind_block = WindBlock(
            blocks[0].begin_time,
            blocks[1].end_time,
            self.wind_type,
            self.flag,
            wf_periods,
            wd_periods,
        )

        return wind_block

    def summarize(self, reference_datetime: Datetime) -> dict:
        """Summarise tha WindBlock as a dictionary."""
        summary: dict = {}

        summary.update(
            {
                self.WD_PERIODS: [
                    p.summarize(reference_datetime) for p in self.wd_periods
                ],
                self.WF_PERIODS: [
                    p.summarize(reference_datetime) for p in self.wf_periods
                ],
                self.TIME_DESC: self.period.describe(reference_datetime),
            }
        )

        return summary

    def __hash__(self) -> int:
        """Hash the WindBlock instance."""
        return hash(
            (
                self.begin_time,
                self.end_time,
                self._wind_type,
                self._flag,
            )
        )

    def __eq__(self, other: WindBlock) -> bool:
        """Check WindBlock equality."""
        if isinstance(other, WindBlock) is False:
            return False
        return (
            self.begin_time == other.begin_time
            and self.end_time == other.end_time
            and self._wind_type == other.wind_type
            and self._flag == other.flag
            and self.wf_periods == other.wf_periods
            and self.wd_periods == other.wd_periods
        )

    def __repr__(self) -> str:
        """Serialize a WindBlock as a string representation."""
        return (
            f"{self.__class__.__name__}(begin_time={self.begin_time}, "
            f"end_time={self.end_time}, duration={self.duration}, "
            f"wind_type={self._wind_type}, flagged={self._flag}, "
            f"wind_direction_periods={self.wd_periods}, "
            f"wind_force_periods={self.wf_periods})"
        )

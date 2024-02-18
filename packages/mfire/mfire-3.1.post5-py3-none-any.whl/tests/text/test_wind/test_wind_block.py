import pytest

from mfire.text.wind.exceptions import WindSynthesisError
from mfire.text.wind.reducers.wind_summary_builder.case3.wind_block import WindBlock
from mfire.text.wind.reducers.wind_summary_builder.helpers import WindType
from mfire.text.wind.reducers.wind_summary_builder.wind_direction import (
    WindDirection,
    WindDirectionPeriod,
)
from mfire.text.wind.reducers.wind_summary_builder.wind_force import (
    WindForce,
    WindForcePeriod,
)
from mfire.utils.date import Datetime, Timedelta


class TestWindBlock:

    BEGIN_TIME: Datetime = Datetime(2023, 1, 1, 0, 0, 0)
    END_TIME: Datetime = Datetime(2023, 1, 1, 9, 0, 0)
    WIND_BLOCK: WindBlock = WindBlock(BEGIN_TIME, END_TIME, WindType.TYPE_3)

    def test_creation(self):

        assert self.WIND_BLOCK.begin_time == self.BEGIN_TIME
        assert self.WIND_BLOCK.end_time == self.END_TIME
        assert self.WIND_BLOCK.duration == Timedelta(self.END_TIME - self.BEGIN_TIME)
        assert self.WIND_BLOCK.flag is False

    def test_wd_period(self):
        wd_period = WindDirectionPeriod(
            Datetime(2023, 1, 1, 2, 0, 0),
            Datetime(2023, 1, 1, 4, 0, 0),
            WindDirection([10.0, 10.0]),
        )
        wd_periods = [wd_period]
        self.WIND_BLOCK.wd_periods = wd_periods
        assert self.WIND_BLOCK.wd_periods == wd_periods

        self.WIND_BLOCK.wd_periods = []
        assert self.WIND_BLOCK.wd_periods == []

        self.WIND_BLOCK.wd_periods = None
        assert self.WIND_BLOCK.wd_periods == []

    @pytest.mark.parametrize(
        "wd_periods, exception",
        [
            (
                # 1 WindForcePeriod: bad type
                [
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 7, 0, 0),
                        Datetime(2023, 1, 1, 9, 0, 0),
                        WindForce(35.0),
                    ),
                ],
                TypeError,
            ),
            (
                # 1 WindDirectionPeriod with a begin_time < block begin_time
                [
                    WindDirectionPeriod(
                        Datetime(2022, 12, 31, 22, 0, 0),
                        Datetime(2023, 1, 1, 8, 0, 0),
                        WindDirection([10.0, 10.0]),
                    ),
                ],
                WindSynthesisError,
            ),
            (
                # 1 WindDirectionPeriod with an end_time > block begin_time
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 0, 0, 0),
                        Datetime(2023, 1, 1, 10, 59, 59),
                        WindDirection([10.0, 10.0]),
                    ),
                ],
                WindSynthesisError,
            ),
            (
                # 1 WindDirectionPeriod with an end_time > block end_time
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 7, 0, 0),
                        Datetime(2023, 1, 1, 23, 0, 0),
                        WindDirection([10.0, 10.0]),
                    ),
                ],
                WindSynthesisError,
            ),
            (
                # 2 unordered WindDirectionPeriod
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 7, 0, 0),
                        Datetime(2023, 1, 1, 9, 0, 0),
                        WindDirection([10.0, 10.0]),
                    ),
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 2, 0, 0),
                        Datetime(2023, 1, 1, 5, 0, 0),
                        WindDirection([10.0, 10.0]),
                    ),
                ],
                WindSynthesisError,
            ),
        ],
    )
    def test_wd_period_exceptions(self, wd_periods, exception):
        with pytest.raises(exception):
            self.WIND_BLOCK.wd_periods = wd_periods

    def test_wf_period(self):
        wf_period = WindForcePeriod(
            Datetime(2023, 1, 1, 2, 0, 0),
            Datetime(2023, 1, 1, 4, 0, 0),
            WindForce(35.0),
        )
        wf_periods = [wf_period]
        self.WIND_BLOCK.wf_periods = wf_periods
        assert self.WIND_BLOCK.wf_periods == wf_periods

        self.WIND_BLOCK.wf_periods = []
        assert self.WIND_BLOCK.wf_periods == []

        self.WIND_BLOCK.wf_periods = None
        assert self.WIND_BLOCK.wf_periods == []

    @pytest.mark.parametrize(
        "wf_periods, exception",
        [
            (
                # 1 WindDirectionPeriod: bad type
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 7, 0, 0),
                        Datetime(2023, 1, 1, 9, 0, 0),
                        WindDirection([10.0, 10.0]),
                    ),
                ],
                TypeError,
            ),
            (
                # 1 WindForcePeriod with a begin_time < block begin_time
                [
                    WindForcePeriod(
                        Datetime(2022, 12, 31, 22, 0, 0),
                        Datetime(2023, 1, 1, 8, 0, 0),
                        WindForce(35.0),
                    ),
                ],
                WindSynthesisError,
            ),
            (
                # 1 WindForcePeriod with an end_time > block end_time
                [
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 7, 0, 0),
                        Datetime(2023, 1, 1, 23, 0, 0),
                        WindForce(35.0),
                    ),
                ],
                WindSynthesisError,
            ),
            (
                # 1 WindForcePeriod with an end_time > block begin_time
                [
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 0, 0, 0),
                        Datetime(2023, 1, 1, 10, 59, 59),
                        WindForce(35.0),
                    ),
                ],
                WindSynthesisError,
            ),
            (
                # 2 unordered WindForcePeriod
                [
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 7, 0, 0),
                        Datetime(2023, 1, 1, 9, 0, 0),
                        WindForce(35.0),
                    ),
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 2, 0, 0),
                        Datetime(2023, 1, 1, 5, 0, 0),
                        WindForce(35.0),
                    ),
                ],
                WindSynthesisError,
            ),
        ],
    )
    def test_wf_period_exceptions(self, wf_periods, exception):
        with pytest.raises(exception):
            self.WIND_BLOCK.wf_periods = wf_periods

    @pytest.mark.parametrize(
        "blocks, expected",
        [
            (
                [
                    WindBlock(
                        Datetime(2023, 1, 2, 0, 0, 0),
                        Datetime(2023, 1, 2, 10, 0, 0),
                        WindType.TYPE_3,
                        True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 0, 0, 0),
                                Datetime(2023, 1, 2, 8, 0, 0),
                                WindForce(35.0),
                            ),
                        ],
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 1, 0, 0),
                                Datetime(2023, 1, 2, 6, 0, 0),
                                WindDirection([10.0, 10.0]),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 12, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        False,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 13, 0, 0),
                                Datetime(2023, 1, 2, 14, 0, 0),
                                WindForce(45.0),
                            ),
                        ],
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 13, 0, 0),
                                Datetime(2023, 1, 2, 18, 0, 0),
                                WindDirection([10.0, 10.0]),
                            )
                        ],
                    ),
                ],
                WindBlock(
                    Datetime(2023, 1, 2, 0, 0, 0),
                    Datetime(2023, 1, 2, 23, 0, 0),
                    WindType.TYPE_3,
                    True,
                    wf_periods=[
                        WindForcePeriod(
                            Datetime(2023, 1, 2, 0, 0, 0),
                            Datetime(2023, 1, 2, 8, 0, 0),
                            WindForce(35.0),
                        ),
                        WindForcePeriod(
                            Datetime(2023, 1, 2, 13, 0, 0),
                            Datetime(2023, 1, 2, 14, 0, 0),
                            WindForce(45.0),
                        ),
                    ],
                    wd_periods=[
                        WindDirectionPeriod(
                            Datetime(2023, 1, 2, 1, 0, 0),
                            Datetime(2023, 1, 2, 6, 0, 0),
                            WindDirection([10.0, 10.0]),
                        ),
                        WindDirectionPeriod(
                            Datetime(2023, 1, 2, 13, 0, 0),
                            Datetime(2023, 1, 2, 18, 0, 0),
                            WindDirection([10.0, 10.0]),
                        ),
                    ],
                ),
            )
        ],
    )
    def test_merge(self, blocks, expected):
        assert blocks[0].merge(blocks[1]) == expected

    @pytest.mark.parametrize(
        "blocks",
        [
            [
                WindBlock(
                    Datetime(2023, 1, 2, 0, 0, 0),
                    Datetime(2023, 1, 2, 5, 0, 0),
                    WindType.TYPE_3,
                    False,
                ),
                WindBlock(
                    Datetime(2023, 1, 2, 2, 0, 0),
                    Datetime(2023, 1, 2, 10, 0, 0),
                    WindType.TYPE_3,
                    False,
                ),
            ],
            [
                WindBlock(
                    Datetime(2023, 1, 2, 0, 0, 0),
                    Datetime(2023, 1, 2, 5, 0, 0),
                    WindType.TYPE_3,
                    False,
                ),
                WindBlock(
                    Datetime(2023, 1, 2, 2, 0, 0),
                    Datetime(2023, 1, 2, 3, 0, 0),
                    WindType.TYPE_3,
                    False,
                ),
            ],
        ],
    )
    def test_merge_exception(self, blocks):
        with pytest.raises(WindSynthesisError):
            blocks[0].merge(blocks[1])

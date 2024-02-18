"""Unit tests of wind direction classes."""

import copy
from functools import reduce
import numpy as np
import pytest
from typing import Optional

import mfire.utils.mfxarray as xr
from mfire.text.wind.reducers.wind_summary_builder import case3
from mfire.text.wind.reducers.wind_summary_builder.helpers import PandasWindSummary
from mfire.text.wind.reducers.wind_summary_builder.wind_direction import (
    WindDirection,
    WindDirectionPeriod,
    WindDirectionPeriodFinder,
)
from mfire.utils.date import Datetime
from tests.text.utils import generate_valid_times, generate_valid_times_v2

from .mixins import Data1x1, Data2x2
from .utils import add_previous_time_in_pd_summary


class TestWindDirection:
    @pytest.mark.parametrize(
        "degrees, size, lower_bound, upper_bound, middle, sympo_code, check",
        [
            ([0.2, 90.2], 90.0, 0.2, 90.2, 45.2, 2, True),
            ([0.2, 90.3], 90.1, 0.2, 90.3, 45.25, 2, False),
            ([0.2, 100.2], 100.0, 0.2, 100.2, 50.2, 2, False),
            ([330.0, 10.0], 40.0, -30.0, 10.0, 350.0, 0, True),
            ([320.0, 10.5], 50.5, -40.0, 10.5, 345.25, 15, True),
            ([210.0, 355.3, 10.0], 160.0, -150.0, 10.0, 290.0, 13, False),
            ([340.0, 341.3, 342.0], 2.0, 340.0, 342.0, 341.0, 15, True),
            ([350.0, 351.3, 352.0], 2.0, 350.0, 352.0, 351.0, 0, True),
            ([360.0, 360.0], 0.0, 360.0, 360.0, 0.0, 0, True),
            ([360.0, 10.0], 10.0, 10.0, 360.0, 5.0, 0, True),
            ([350.0, 10.0], 20.0, -10.0, 10.0, 0.0, 0, True),
        ],
    )
    def test_creation(
        self, degrees, size, lower_bound, upper_bound, middle, sympo_code, check
    ):
        wd: WindDirection = WindDirection(degrees)
        assert wd.size == size
        assert wd.lower_bound == lower_bound
        assert wd.upper_bound == upper_bound
        assert wd.middle == middle
        assert wd.sympo_code == sympo_code
        assert wd.check_size(WindDirectionPeriodFinder.TERM_DIRECTION_SIZE_MAX) == check

    @pytest.mark.parametrize(
        "wind_directions, res",
        [
            (
                [WindDirection([10, 50]), WindDirection([21, 64.3])],
                WindDirection([10, 64.3]),
            ),
            (
                [WindDirection([360.0, 10.0]), WindDirection([11.0, 20.0])],
                WindDirection([360, 20.0]),
            ),
            (
                [WindDirection([360.0, 360.0]), WindDirection([360.0, 360.0])],
                WindDirection([360, 360.0]),
            ),
            (
                [WindDirection([350.0, 360.0]), WindDirection([10.0, 20.0])],
                WindDirection([350, 20.0]),
            ),
            (
                [WindDirection([350.0, 10.0]), WindDirection([15.0, 20.0])],
                WindDirection([350, 20.0]),
            ),
        ],
    )
    def test_sum(self, wind_directions, res):
        assert reduce(lambda wd1, wd2: wd1 + wd2, wind_directions) == res

    @pytest.mark.parametrize(
        "d1, d2, res",
        [
            (WindDirection([0.1]), WindDirection([0.1]), True),
            (WindDirection([0.1]), WindDirection([0.1, 22.4]), True),
            (WindDirection([0.1]), WindDirection([90.1]), False),
        ],
    )
    def test_equality(self, d1, d2, res):
        if res is True:
            assert d1 == d2
        else:
            assert d1 != d2

    @pytest.mark.parametrize(
        "d1, d2, res",
        [
            (WindDirection([0.1]), WindDirection([0.1]), True),
            (WindDirection([0.1]), WindDirection([157.6]), False),
            (WindDirection([0.1]), WindDirection([180.0]), True),
            (WindDirection([-30.0]), WindDirection([150.0]), True),
        ],
    )
    def test_is_opposite_to(self, d1, d2, res):
        assert d1.is_opposite_to(d2) == res


class TestWindDirectionPeriod:

    SIZE_MAX = WindDirectionPeriodFinder.MULTIPLE_TERMS_DIRECTION_SIZE_MAX
    WIND_DIRECTION = WindDirection([10.0, 64.3])
    WIND_DIRECTION_PERIOD = WindDirectionPeriod(
        Datetime(2023, 1, 1, 10, 0, 0),
        Datetime(2023, 1, 1, 11, 0, 0),
        WIND_DIRECTION,
    )

    @pytest.mark.parametrize(
        "begin_time, end_time",
        [
            (
                Datetime(2023, 1, 1, 11, 0, 0),
                Datetime(2023, 1, 1, 10, 0, 0),
            ),
            (
                Datetime(2023, 1, 1, 11, 0, 0),
                Datetime(2023, 1, 1, 11, 59, 59),
            ),
            (
                Datetime(2023, 1, 1, 11, 0, 0),
                Datetime(2023, 1, 1, 11, 0, 0),
            ),
        ],
    )
    def test_creation_exception(self, begin_time, end_time):
        with pytest.raises(ValueError):
            WindDirectionPeriod(
                begin_time,
                end_time,
                self.WIND_DIRECTION,
            )

    @pytest.mark.parametrize(
        "period, res_exp, period_exp",
        [
            (
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 11, 0, 0),
                    Datetime(2023, 1, 1, 12, 0, 0),
                    WindDirection([10.0, 10.0 + SIZE_MAX - 0.1]),
                ),
                True,
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 10, 0, 0),
                    Datetime(2023, 1, 1, 12, 0, 0),
                    WindDirection([10.0, 10.0 + SIZE_MAX - 0.1]),
                ),
            ),
            (
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 11, 0, 0),
                    Datetime(2023, 1, 1, 12, 0, 0),
                    WindDirection([10.0, 10.0 + SIZE_MAX]),
                ),
                True,
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 10, 0, 0),
                    Datetime(2023, 1, 1, 12, 0, 0),
                    WindDirection([10.0, 10.0 + SIZE_MAX]),
                ),
            ),
            (
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 9, 0, 0),
                    Datetime(2023, 1, 1, 11, 0, 0),
                    WindDirection([10.0, 10.0 + SIZE_MAX + 0.1]),
                ),
                False,
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 10, 0, 0),
                    Datetime(2023, 1, 1, 11, 0, 0),
                    WIND_DIRECTION,
                ),
            ),
            (
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 11, 0, 0),
                    Datetime(2023, 1, 1, 12, 0, 0),
                    WindDirection([10.0, 10.0 + SIZE_MAX + 0.1]),
                ),
                False,
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 10, 0, 0),
                    Datetime(2023, 1, 1, 11, 0, 0),
                    WIND_DIRECTION,
                ),
            ),
        ],
    )
    def test_update(
        self,
        period: WindDirectionPeriod,
        res_exp: bool,
        period_exp: WindDirectionPeriod,
    ):
        wind_dir_period = copy.deepcopy(self.WIND_DIRECTION_PERIOD)
        res = wind_dir_period.update(period, size_max=self.SIZE_MAX)
        assert res == res_exp
        assert wind_dir_period == period_exp

    @pytest.mark.parametrize(
        "wd_p1, wd_p2, wd_p_exp",
        [
            (
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 4, 0, 0),
                    WindDirection([10.0, 10.0]),
                ),
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 6, 0, 0),
                    Datetime(2023, 1, 1, 10, 0, 0),
                    WindDirection([10.0, 10.0]),
                ),
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 10, 0, 0),
                    WindDirection([10.0, 10.0]),
                ),
            ),
        ],
    )
    def test_addition(self, wd_p1, wd_p2, wd_p_exp):
        assert wd_p1 + wd_p2 == wd_p_exp

    @pytest.mark.parametrize(
        "wd_p1, wd_p2, res",
        [
            (
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 4, 0, 0),
                    WindDirection([10.0, 10.0]),
                ),
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 6, 0, 0),
                    Datetime(2023, 1, 1, 10, 0, 0),
                    WindDirection([10.0, 10.0]),
                ),
                True,
            ),
            (
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 4, 0, 0),
                    WindDirection([0.1, 0.1]),
                ),
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 6, 0, 0),
                    Datetime(2023, 1, 1, 10, 0, 0),
                    WindDirection([180.0, 180.0]),
                ),
                False,
            ),
        ],
    )
    def test_has_same_direction_than(self, wd_p1, wd_p2, res):
        assert wd_p1.has_same_direction_than(wd_p2) == res

    @pytest.mark.parametrize(
        "wd_p1, wd_p2, res",
        [
            (
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 4, 0, 0),
                    WindDirection([0.1]),
                ),
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 6, 0, 0),
                    Datetime(2023, 1, 1, 10, 0, 0),
                    WindDirection([0.1]),
                ),
                True,
            ),
            (
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 4, 0, 0),
                    WindDirection([0.1]),
                ),
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 6, 0, 0),
                    Datetime(2023, 1, 1, 10, 0, 0),
                    WindDirection([157.5]),
                ),
                False,
            ),
            (
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 4, 0, 0),
                    WindDirection([0.1]),
                ),
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 6, 0, 0),
                    Datetime(2023, 1, 1, 10, 0, 0),
                    WindDirection([180.0]),
                ),
                True,
            ),
            (
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 4, 0, 0),
                    WindDirection([-30.0]),
                ),
                WindDirectionPeriod(
                    Datetime(2023, 1, 1, 6, 0, 0),
                    Datetime(2023, 1, 1, 10, 0, 0),
                    WindDirection([150.0]),
                ),
                True,
            ),
        ],
    )
    def test_has_opposite_direction_to(self, wd_p1, wd_p2, res):
        assert wd_p1.has_opposite_direction_to(wd_p2) == res


class TestWindDirectionPeriodFinder(Data2x2):
    """ "Test WindDirectionPeriodFinder with 2x2 data."""

    SIZE_MAX = WindDirectionPeriodFinder.MULTIPLE_TERMS_DIRECTION_SIZE_MAX

    class WindDirectionPeriodFinderTester(WindDirectionPeriodFinder):
        """WindDirectionPeriodFinderTester class.

        For more simplicity, PERIOD_DURATION_MIN is reduced from 3 to 2 hours.
        """

        PERIOD_DURATION_MIN: np.timedelta64 = np.timedelta64(2, "h")
        PERCENT_MIN: float = 100.0

    @pytest.mark.parametrize(
        "data, valid_times, valid_times_kept, expected",
        [
            # term 0: wd = [10., 22.] OK, term 1: wd = [19.6, 22.3] OK
            # [10., 22.3] has size 12.3 <= MULTIPLE_TERMS_DIRECTION_SIZE_MAX
            # ==> 1 WindDirectionPeriod found
            (
                [[[10.0, 22.0], [np.nan, 21.0]], [[np.nan, 19.6], [np.nan, 22.3]]],
                generate_valid_times(periods=2),
                generate_valid_times(periods=2),
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 23),
                        Datetime(2023, 1, 2, 1),
                        WindDirection([10.0, 22.3]),
                    )
                ],
            ),
            (
                # term 0: wd = [10., 22.] OK, term 1: wd = [77.5, 10. + SIZE_MAX] OK
                # [10., 10. + SIZE_MAX] has size MULTIPLE_TERMS_DIRECTION_SIZE_MAX
                # ==> 1 WindDirectionPeriod found
                [
                    [[10.0, 22.0], [np.nan, 21.0]],
                    [[np.nan, 77.5], [np.nan, 10.0 + SIZE_MAX]],
                ],
                generate_valid_times(periods=2),
                generate_valid_times(periods=2),
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 23),
                        Datetime(2023, 1, 2, 1),
                        WindDirection([10.0, 145.0]),
                    )
                ],
            ),
            (
                # term 0: wd = [10., 22.] OK
                # term 1: wd = [77.5, 167.6] OK
                # term 2: [10., 10. + SIZE_MAX + 0.1] has a size >
                # MULTIPLE_TERMS_DIRECTION_SIZE_MAX ==> no wind direction for it
                # ==> 0 WindDirectionPeriod found
                [
                    [[10.0, 22.0], [np.nan, 21.0]],
                    [[np.nan, 77.5], [np.nan, 10.0 + SIZE_MAX + 0.1]],
                ],
                generate_valid_times(periods=2),
                generate_valid_times(periods=2),
                [],
            ),
            (
                # term 0: wd = [10., 22.] OK, term 1: wd = [2.3, 93.] NOK because size
                # 90.7 > TERM_DIRECTION_SIZE_MAX ==> 0 WindDirectionPeriod found
                [[[10.0, 22.0], [np.nan, 21.0]], [[np.nan, 2.3], [93.0, 84.6]]],
                generate_valid_times(periods=2),
                generate_valid_times(periods=2),
                [],
            ),
            (
                # term 0: wd = [10., 22.] OK
                # term 1: wd = [77.5, 10. + SIZE_MAX] OK,
                # term 2: wd = [90.2, 101.] OK
                # [10., 10. + SIZE_MAX] has size  MULTIPLE_TERMS_DIRECTION_SIZE_MAX
                # ==> 1 WindDirectionPeriod found
                [
                    [[10.0, 22.0], [np.nan, 21.0]],
                    [[np.nan, 77.5], [np.nan, 10.0 + SIZE_MAX]],
                    [[np.nan, 90.2], [np.nan, 101.0]],
                ],
                generate_valid_times(periods=3),
                generate_valid_times(periods=3),
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 23),
                        Datetime(2023, 1, 2, 2),
                        WindDirection([10.0, 10.0 + SIZE_MAX]),
                    )
                ],
            ),
            (
                # term 0: wd = [10., 22.]
                # term 1: wd = [170.0, 173.0]
                # term 2: wd = [90.2, 101.]
                # The wind direction changes on all terms => no WindDirectionPeriod
                [
                    [[10.0, 22.0], [np.nan, 21.0]],
                    [[np.nan, 170.0], [np.nan, 173.0]],
                    [[np.nan, 90.2], [np.nan, 101.0]],
                ],
                generate_valid_times(periods=3),
                generate_valid_times(periods=3),
                [],
            ),
            (
                # term 0: wd = [10., 22.]
                # term 1: wd = [170.0, 173.0]
                # term 2: wd = [10., 22.]
                # term 3: wd = [170.0, 173.0]
                # No WindDirectionPeriod
                [
                    [[10.0, 22.0], [np.nan, 21.0]],
                    [[np.nan, 170.0], [np.nan, 173.0]],
                    [[10.0, 22.0], [np.nan, 21.0]],
                    [[np.nan, 170.0], [np.nan, 173.0]],
                ],
                generate_valid_times(periods=4),
                generate_valid_times(periods=4),
                [],
            ),
            (
                # term 0: wd = [10., 22.] OK,
                # term 1: wd = [6., 18.] OK,
                # term 2: wd = [77.5, 10. + SIZE_MAX + 1] OK,
                # term 3: wd = [90.2, 101.] OK
                # ==> 2 WindDirectionPeriod found:
                # - wind dir [6.0, 22.0] for 2 hours,
                # - wind dir [77.5, 10. + SIZE_MAX + 1] for 2 hours
                [
                    [[10.0, 22.0], [np.nan, 21.0]],
                    [[6.0, 18.0], [np.nan, 17.0]],
                    [[np.nan, 77.5], [np.nan, 10.0 + SIZE_MAX + 1]],
                    [[np.nan, 90.2], [np.nan, 101.0]],
                ],
                generate_valid_times(periods=4),
                generate_valid_times(periods=4),
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 23),
                        Datetime(2023, 1, 2, 1),
                        WindDirection([6.0, 22.0]),
                    ),
                    WindDirectionPeriod(
                        Datetime(2023, 1, 2, 1),
                        Datetime(2023, 1, 2, 3),
                        WindDirection([77.5, 10.0 + SIZE_MAX + 1]),
                    ),
                ],
            ),
            (
                # term 0: wd = [10., 22.] OK, term 1: wd = [6., 18.] OK,
                # term 2: wd = [77.5, 10. + SIZE_MAX + 1] OK,
                # term 2: wd = [90.2, 101.] OK
                # We are looking for WindDirectionPeriod only on the 2 first terms
                # ==> 1 WindDirectionPeriod found: [6.0, 22.0]
                [
                    [[10.0, 22.0], [np.nan, 21.0]],
                    [[6.0, 18.0], [np.nan, 17.0]],
                    [[np.nan, 77.5], [np.nan, 10.0 + SIZE_MAX + 1]],
                    [[np.nan, 90.2], [np.nan, 101.0]],
                ],
                generate_valid_times(periods=4),
                generate_valid_times(periods=2),
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 23),
                        Datetime(2023, 1, 2, 1),
                        WindDirection([6.0, 22.0]),
                    )
                ],
            ),
        ],
    )
    def test_period_finder(self, data: list, valid_times, valid_times_kept, expected):
        data_array: xr.DataArray = self._create_param_data_array(
            np.array(data), valid_times
        )

        # Create PandasWindSummary
        pd_summary: PandasWindSummary = PandasWindSummary(valid_time=valid_times)
        add_previous_time_in_pd_summary(pd_summary, valid_times)

        period_finder = self.WindDirectionPeriodFinderTester.from_data_array(
            data_array, pd_summary, valid_times_kept
        )
        res = period_finder.run()
        assert res == expected


class TestWindDirectionPeriodFinder1x1(Data1x1, TestWindDirectionPeriodFinder):
    """Test WindDirectionPeriodFinder with 1x1 data."""

    @pytest.mark.parametrize(
        "data, valid_times, valid_times_kept, expected",
        [
            # No WindDirectionPeriod
            (
                [10.0, 180.0, 190.0, 180.0, 180.0],
                generate_valid_times(periods=5),
                generate_valid_times(periods=2, freq="2H"),
                [],
            ),
            # No WindDirectionPeriod
            (
                [10.0, 190.0, 10.0, 190.0, 10.0],
                generate_valid_times(periods=5),
                generate_valid_times(periods=5),
                [],
            ),
            # No WindDirectionPeriod
            (
                [10.0, 10.0, 190.0, 190.0, 10.0],
                generate_valid_times(periods=5),
                generate_valid_times(periods=5),
                [],
            ),
            # Same wind direction 10 during 3 hours => 1 WindDirectionPeriod
            (
                [10.0, 180.0, 10.0, 180.0, 180.0],
                generate_valid_times(periods=5),
                generate_valid_times(periods=2, freq="2H"),
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 23),
                        Datetime(2023, 1, 2, 2),
                        WindDirection([10.0]),
                    ),
                ],
            ),
            # Same wind direction 10 during 3 hours => 1 WindDirectionPeriod
            (
                [10.0, 10.0, 10.0, 180.0, 180.0],
                generate_valid_times(periods=5),
                generate_valid_times(periods=3),
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 23),
                        Datetime(2023, 1, 2, 2),
                        WindDirection([10.0]),
                    ),
                ],
            ),
            # Some terms are not covered by a WindDirectionPeriod
            # => no WindDirectionPeriod
            (
                [10.0, 180.0, 10.0, 180.0, 190.0],
                generate_valid_times(periods=5),
                generate_valid_times(periods=3, freq="2H"),
                [],
            ),
            # All terms have a wind direction, but it always changes
            # => no WindDirectionPeriod
            (
                [10.0, 180.0, 10.0, 180.0, 10.0],
                generate_valid_times(periods=5),
                generate_valid_times(periods=5),
                [],
            ),
            # One term has no wind direction => no WindDirectionPeriod
            (
                [10.0, 180.0, np.nan, 180.0, 10.0],
                generate_valid_times(periods=5),
                generate_valid_times(periods=5),
                [],
            ),
            # One term has no wind direction => no WindDirectionPeriod
            (
                [10.0, 10.0, 10.0, 180.0, np.nan],
                generate_valid_times(periods=5),
                generate_valid_times(periods=5),
                [],
            ),
            # Kept 1-hours terms: [10.0, x, 10.0, 157.5, 157.5, 157.5]
            # => 2 WindDirectionPeriod: 10 and 157.5
            (
                [10.0, 157.5, 10.0, 157.5, 157.5, 157.5],
                generate_valid_times(periods=6),
                generate_valid_times_v2("2023-01-02", (2, "2H"), (3, "H")),
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 23),
                        Datetime(2023, 1, 2, 2),
                        WindDirection([10.0]),
                    ),
                    WindDirectionPeriod(
                        Datetime(2023, 1, 2, 2),
                        Datetime(2023, 1, 2, 5),
                        WindDirection([157.5]),
                    ),
                ],
            ),
        ],
    )
    def test_period_finder(self, data: list, valid_times, valid_times_kept, expected):
        super().test_period_finder(data, valid_times, valid_times_kept, expected)

    @pytest.mark.parametrize(
        "data, valid_times, valid_times_kept, expected",
        [
            (
                [10.0, 10.0],
                generate_valid_times(periods=2, freq="2H"),
                generate_valid_times(periods=2, freq="2H"),
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 22),
                        Datetime(2023, 1, 2, 2),
                        WindDirection([10.0]),
                    )
                ],
            ),
            (
                [0.1] * 2 + [157.5],
                generate_valid_times(periods=3, freq="3H"),
                generate_valid_times(periods=3, freq="3H"),
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 21),
                        Datetime(2023, 1, 2, 3),
                        WindDirection([0.1]),
                    ),
                    WindDirectionPeriod(
                        Datetime(2023, 1, 2, 3),
                        Datetime(2023, 1, 2, 6),
                        WindDirection([157.5]),
                    ),
                ],
            ),
        ],
    )
    def test_period_finder_variable_step(
        self, data: list, valid_times, valid_times_kept, expected
    ):
        super().test_period_finder(data, valid_times, valid_times_kept, expected)


class TestHighWindDirectionPeriodFinder(TestWindDirectionPeriodFinder):
    """Test HighWindDirectionPeriodFinder."""

    class WindDirectionPeriodFinderTester(case3.HighWindDirectionPeriodFinder):
        pass

    @pytest.mark.parametrize(
        "data, valid_times, valid_times_kept, expected",
        [
            # The 1st term has no WindDirection => no WindDirection Period
            (
                [[[0.1, 0.1], [160.0, 0.1]], [[0.1, 150.0], [0.1, 0.1]]],
                generate_valid_times(periods=2),
                generate_valid_times(periods=2),
                [],
            ),
            # The beginning time of the 1st initial period does not match with the
            # periods return by _find_periods => no WindDirection Period
            (
                [
                    [[0.1, 0.1], [0.1, 0.1]],
                    [[170.0, 170.0], [170.0, 170.0]],
                    [[170.0, 170.0], [170.0, 170.0]],
                    [[170.0, 170.0], [170.0, 170.0]],
                ],
                generate_valid_times(periods=4),
                generate_valid_times(periods=4),
                [],
            ),
            (
                # All terms have the same WindDirection: _find_periods find a 3-hours
                # WindDirectionPeriod
                [
                    [[170.0, 170.0], [170.0, 170.0]],
                    [[170.0, 170.0], [170.0, 170.0]],
                    [[170.0, 170.0], [170.0, 170.0]],
                ],
                generate_valid_times(periods=3),
                generate_valid_times(periods=3),
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 23),
                        Datetime(2023, 1, 2, 2),
                        WindDirection([170.0]),
                    )
                ],
            ),
            (
                # All terms have the same WindDirection but _find_periods find a 2-hours
                # period which is so short => WindDirectionPeriod
                [
                    [[170.0, 170.0], [170.0, 170.0]],
                    [[170.0, 170.0], [170.0, 170.0]],
                ],
                generate_valid_times(periods=2),
                generate_valid_times(periods=2),
                [],
            ),
            (
                [
                    [[0.1, 0.1], [160.0, 0.1]],
                    [[0.1, 150.0], [0.1, 0.1]],
                    [[0.1, 155.0], [0.1, 0.1]],
                ],
                generate_valid_times(periods=3),
                generate_valid_times(periods=3),
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 23),
                        Datetime(2023, 1, 2, 2),
                        WindDirection([0.1]),
                    )
                ],
            ),
            (
                [
                    [[0.1, 0.1], [160.0, 0.1]],
                    [[180.0, 180.0], [180.0, 0.1]],
                    [[0.1, 150.0], [0.1, 0.1]],
                ],
                generate_valid_times(periods=3),
                generate_valid_times(periods=2, freq="2H"),
                [
                    WindDirectionPeriod(
                        Datetime(2023, 1, 1, 23),
                        Datetime(2023, 1, 2, 2),
                        WindDirection([0.1]),
                    )
                ],
            ),
            (
                [[[0.1, 0.1], [160.0, 0.1]], [[150.0, 150.0], [150.0, 0.1]]],
                generate_valid_times(periods=2),
                generate_valid_times(periods=2),
                [],
            ),
        ],
    )
    def test_period_finder(self, data, valid_times, valid_times_kept, expected):
        super().test_period_finder(data, valid_times, valid_times_kept, expected)


class TestWindDirectionPeriodsInitializerWithNoneTermPeriod(Data1x1):
    """Test WindDirectionPeriodsInitializer with None term periods."""

    class WindDirectionPeriodsInitializerTester(
        WindDirectionPeriodFinder.WIND_PERIOD_INITIALIZER
    ):
        """Inherits of WindDirectionPeriodsInitializer."""

        @classmethod
        def _get_term_period(
            cls,
            term_data: xr.DataArray,
            pd_summary: PandasWindSummary,
        ) -> Optional[WindDirectionPeriod]:
            """Return always None."""
            return None

    class HighWindDirectionPeriodsInitializerTester(
        case3.HighWindDirectionPeriodFinder.WIND_PERIOD_INITIALIZER
    ):
        """Inherits of HighWindDirectionPeriodFinder."""

        @classmethod
        def _get_term_period(
            cls,
            term_data: xr.DataArray,
            pd_summary: PandasWindSummary,
        ) -> Optional[WindDirectionPeriod]:
            """Return always None."""
            return None

    @pytest.mark.parametrize(
        "data, valid_times",
        [
            (
                [10.0, 10.0],
                generate_valid_times(periods=2),
            ),
        ],
    )
    def test(self, data: list, valid_times):
        """Test wind direction period initializers."""

        data_array: xr.DataArray = self._create_param_data_array(
            np.array(data), valid_times
        )

        # Create PandasWindSummary
        pd_summary: PandasWindSummary = PandasWindSummary(valid_time=valid_times)
        add_previous_time_in_pd_summary(pd_summary, valid_times)

        for initializer in [
            self.WindDirectionPeriodsInitializerTester,
            self.HighWindDirectionPeriodsInitializerTester,
        ]:
            term_periods = initializer.get_term_periods(
                data_array, pd_summary, valid_times
            )
            assert term_periods == []

"""Unit tests of wind force classes."""

import copy
from functools import reduce
import numpy as np
import pytest
from typing import Optional

import mfire.utils.mfxarray as xr
from mfire.text.wind.reducers.wind_summary_builder.helpers import PandasWindSummary
from mfire.text.wind.reducers.wind_summary_builder.wind_force import (
    WindForce,
    WindForcePeriod,
    WindForcePeriodFinder,
)
from mfire.utils.date import Datetime
from tests.text.utils import generate_valid_times, generate_valid_times_v2

from .factories import CompositeFactory1x100
from .mixins import Data1x1
from .utils import add_previous_time_in_pd_summary


class TestWindForce:
    @pytest.mark.parametrize(
        "force, repr_value_exp, interval_exp",
        [
            (50.0, 50, (50, 55)),
            (54.9, 50, (50, 55)),
            (55.0, 55, (55, 60)),
        ],
    )
    def test_creation_default_precision(self, force, repr_value_exp, interval_exp):
        wf = WindForce(force)
        assert wf.repr_value == repr_value_exp
        assert wf.interval == interval_exp

    @pytest.mark.parametrize(
        "force, precision, repr_value_exp, interval_exp",
        [
            (50.0, 5, 50, (50, 55)),
            (50.0, 10, 50, (50, 60)),
        ],
    )
    def test_creation(self, force, precision, repr_value_exp, interval_exp):
        wf = WindForce(force, precision)
        assert wf.repr_value == repr_value_exp
        assert wf.interval == interval_exp

    @pytest.mark.parametrize(
        "valid_times, data_wf, wind_force_exp",
        [
            (
                generate_valid_times(periods=1),
                np.arange(1.0, 101.0, 1, dtype=np.float64),
                WindForce(95.0),
            ),
        ],
    )
    def test_creation_from_term(self, valid_times, data_wf, wind_force_exp):
        composite = CompositeFactory1x100().get(
            valid_times=valid_times,
            data_wind=data_wf,
        )
        dataset = composite.compute()
        data_array: xr.DataArray = dataset["wind"].sel(valid_time=valid_times[0])
        wind_force: WindForce = WindForce.from_term_data_array(data_array)
        assert wind_force == wind_force_exp

    def test_comparison(self):
        assert WindForce(50) == WindForce(50)
        assert WindForce(50) <= WindForce(50)
        assert WindForce(50) >= WindForce(50)

        assert WindForce(50) == WindForce(54)

        assert WindForce(50) < WindForce(60)
        assert WindForce(60) > WindForce(50)

    def test_addition(self):
        assert WindForce(30) + WindForce(30) == WindForce(30)
        assert WindForce(30) + WindForce(34) == WindForce(30)
        assert WindForce(30) + WindForce(35) == WindForce(30, precision=10)
        assert WindForce(30, precision=10) + WindForce(35, precision=15) == WindForce(
            30, precision=20
        )
        assert WindForce(30, precision=10) + WindForce(50, precision=15) == WindForce(
            30, precision=35
        )


class TestWindForcePeriod:

    WIND_FORCE = WindForce(52.0)
    WIND_FORCE_PERIOD = WindForcePeriod(
        Datetime(2023, 1, 1, 10, 0, 0),
        Datetime(2023, 1, 1, 11, 0, 0),
        WIND_FORCE,
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
            WindForcePeriod(
                begin_time,
                end_time,
                self.WIND_FORCE,
            )

    @pytest.mark.parametrize(
        "period, res_exp, period_exp",
        [
            (
                WindForcePeriod(
                    Datetime(2023, 1, 1, 11, 0, 0),
                    Datetime(2023, 1, 1, 12, 0, 0),
                    WindForce(50.0),
                ),
                True,
                WindForcePeriod(
                    Datetime(2023, 1, 1, 10, 0, 0),
                    Datetime(2023, 1, 1, 12, 0, 0),
                    WIND_FORCE,
                ),
            ),
            (
                WindForcePeriod(
                    Datetime(2023, 1, 1, 11, 0, 0),
                    Datetime(2023, 1, 1, 12, 0, 0),
                    WindForce(54.1),
                ),
                True,
                WindForcePeriod(
                    Datetime(2023, 1, 1, 10, 0, 0),
                    Datetime(2023, 1, 1, 12, 0, 0),
                    WIND_FORCE,
                ),
            ),
            (
                WindForcePeriod(
                    Datetime(2023, 1, 1, 11, 0, 0),
                    Datetime(2023, 1, 1, 12, 0, 0),
                    WindForce(55.0),
                ),
                False,
                WindForcePeriod(
                    Datetime(2023, 1, 1, 10, 0, 0),
                    Datetime(2023, 1, 1, 11, 0, 0),
                    WIND_FORCE,
                ),
            ),
        ],
    )
    def test_update(
        self,
        period: WindForcePeriod,
        res_exp: bool,
        period_exp: WindForcePeriod,
    ):
        wind_force_period = copy.deepcopy(self.WIND_FORCE_PERIOD)
        res = wind_force_period.update(period)
        assert res == res_exp
        assert wind_force_period == period_exp

    @pytest.mark.parametrize(
        "wf_p1, wf_p2, wf_p_exp",
        [
            (
                WindForcePeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 4, 0, 0),
                    WindForce(20.0),
                ),
                WindForcePeriod(
                    Datetime(2023, 1, 1, 5, 0, 0),
                    Datetime(2023, 1, 1, 7, 0, 0),
                    WindForce(22.0),
                ),
                WindForcePeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 7, 0, 0),
                    WindForce(20.0),
                ),
            ),
            (
                WindForcePeriod(
                    Datetime(2023, 1, 1, 5, 0, 0),
                    Datetime(2023, 1, 1, 7, 0, 0),
                    WindForce(20.0),
                ),
                WindForcePeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 4, 0, 0),
                    WindForce(22.0),
                ),
                WindForcePeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 7, 0, 0),
                    WindForce(20.0),
                ),
            ),
            (
                WindForcePeriod(
                    Datetime(2023, 1, 1, 5, 0, 0),
                    Datetime(2023, 1, 1, 7, 0, 0),
                    WindForce(20.0),
                ),
                WindForcePeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 4, 0, 0),
                    WindForce(30.0),
                ),
                WindForcePeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 7, 0, 0),
                    WindForce(20.0, 15),
                ),
            ),
            (
                WindForcePeriod(
                    Datetime(2023, 1, 1, 5, 0, 0),
                    Datetime(2023, 1, 1, 7, 0, 0),
                    WindForce(20.0, 10),
                ),
                WindForcePeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 4, 0, 0),
                    WindForce(22.0, 10),
                ),
                WindForcePeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 7, 0, 0),
                    WindForce(20.0, 10),
                ),
            ),
        ],
    )
    def test_addition(self, wf_p1, wf_p2, wf_p_exp):
        assert wf_p1 + wf_p2 == wf_p_exp

    @pytest.mark.parametrize(
        "wfp_list, wf_p_exp",
        [
            (
                [
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 0, 0, 0),
                        Datetime(2023, 1, 1, 4, 0, 0),
                        WindForce(20.0),
                    ),
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 5, 0, 0),
                        Datetime(2023, 1, 1, 7, 0, 0),
                        WindForce(22.0),
                    ),
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 15, 0, 0),
                        Datetime(2023, 1, 1, 16, 0, 0),
                        WindForce(20.0),
                    ),
                ],
                WindForcePeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 16, 0, 0),
                    WindForce(20.0),
                ),
            )
        ],
    )
    def test_sum(self, wfp_list, wf_p_exp):
        assert reduce(lambda x, y: x + y, wfp_list) == wf_p_exp

    @pytest.mark.parametrize(
        "wf_p1, wf_p2, wf_p_exp",
        [
            (
                WindForcePeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 4, 0, 0),
                    WindForce(20.0),
                ),
                WindForcePeriod(
                    Datetime(2023, 1, 1, 6, 0, 0),
                    Datetime(2023, 1, 1, 10, 0, 0),
                    WindForce(20.0),
                ),
                True,
            ),
            (
                WindForcePeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 4, 0, 0),
                    WindForce(20.0),
                ),
                WindForcePeriod(
                    Datetime(2023, 1, 1, 6, 0, 0),
                    Datetime(2023, 1, 1, 10, 0, 0),
                    WindForce(24.9),
                ),
                True,
            ),
            (
                WindForcePeriod(
                    Datetime(2023, 1, 1, 0, 0, 0),
                    Datetime(2023, 1, 1, 4, 0, 0),
                    WindForce(20.0),
                ),
                WindForcePeriod(
                    Datetime(2023, 1, 1, 6, 0, 0),
                    Datetime(2023, 1, 1, 10, 0, 0),
                    WindForce(25.0),
                ),
                False,
            ),
        ],
    )
    def test_has_same_direction_than(self, wf_p1, wf_p2, wf_p_exp):
        assert wf_p1.has_same_force_than(wf_p2) == wf_p_exp


class TestWindForcePeriodFinder(Data1x1):
    @pytest.mark.parametrize(
        "data, valid_times, valid_times_kept, periods_exp",
        [
            (
                [40.0],
                generate_valid_times(periods=1),
                generate_valid_times(periods=1),
                [
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 0, 0, 0),
                        WindForce(40.0),
                    )
                ],
            ),
            (
                [40.0, 43.0],
                generate_valid_times(periods=2),
                generate_valid_times(periods=2),
                [
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 1, 0, 0),
                        WindForce(40.0),
                    )
                ],
            ),
            (
                [40.0, 50.0, 60.0],
                generate_valid_times(periods=3),
                generate_valid_times(periods=3),
                [
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 0, 0, 0),
                        WindForce(40.0),
                    ),
                    WindForcePeriod(
                        Datetime(2023, 1, 2, 0, 0, 0),
                        Datetime(2023, 1, 2, 1, 0, 0),
                        WindForce(50.0),
                    ),
                    WindForcePeriod(
                        Datetime(2023, 1, 2, 1, 0, 0),
                        Datetime(2023, 1, 2, 2, 0, 0),
                        WindForce(60.0),
                    ),
                ],
            ),
            (
                [40.0, 42.6, 51.5, 52.0, 53],
                generate_valid_times(periods=5),
                generate_valid_times(periods=5),
                [
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 1, 0, 0),
                        WindForce(40.0),
                    ),
                    WindForcePeriod(
                        Datetime(2023, 1, 2, 1, 0, 0),
                        Datetime(2023, 1, 2, 4, 0, 0),
                        WindForce(50.0),
                    ),
                ],
            ),
            (
                [40.0, 42.6, 51.5, 52.0, 53],
                generate_valid_times(periods=5),
                generate_valid_times(periods=2),
                [
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 1, 0, 0),
                        WindForce(40.0),
                    )
                ],
            ),
            (
                [40.0, 42.6, 10.0, 11.0, 53],
                generate_valid_times(periods=5),
                generate_valid_times_v2("2023-01-02", (2, "H"), (1, "3H")),
                [
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 1, 0, 0),
                        WindForce(40.0),
                    ),
                    WindForcePeriod(
                        Datetime(2023, 1, 2, 3, 0, 0),
                        Datetime(2023, 1, 2, 4, 0, 0),
                        WindForce(50.0),
                    ),
                ],
            ),
            (
                [40.0] * 5,
                generate_valid_times_v2("2023-01-02", (2, "H"), (3, "3H")),
                generate_valid_times_v2("2023-01-02", (2, "H"), (3, "3H")),
                [
                    WindForcePeriod(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 10, 0, 0),
                        WindForce(40.0),
                    ),
                ],
            ),
        ],
    )
    def test_period_finder(self, data, valid_times, valid_times_kept, periods_exp):
        data_array: xr.DataArray = self._create_param_data_array(
            np.array(data), valid_times
        )

        # Create PandasWindSummary
        pd_summary: PandasWindSummary = PandasWindSummary(valid_time=valid_times)
        add_previous_time_in_pd_summary(pd_summary, valid_times)

        period_finder = WindForcePeriodFinder.from_data_array(
            data_array, pd_summary, valid_times_kept
        )

        periods = period_finder.run()
        assert periods == periods_exp


class TestWindForcePeriodsInitializerWithNoneTermPeriod(Data1x1):
    """Test WindDirectionPeriodsInitializer with None term periods."""

    class WindForcePeriodsInitializerTester(
        WindForcePeriodFinder.WIND_PERIOD_INITIALIZER
    ):
        """Inherits of WindDirectionPeriodsInitializer."""

        @classmethod
        def _get_term_period(
            cls,
            term_data: xr.DataArray,
            pd_summary: PandasWindSummary,
        ) -> Optional[WindForcePeriod]:
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
        """Test WindForcePeriodFinder.WIND_PERIOD_INITIALIZER."""

        data_array: xr.DataArray = self._create_param_data_array(
            np.array(data), valid_times
        )

        # Create PandasWindSummary
        pd_summary: PandasWindSummary = PandasWindSummary(valid_time=valid_times)
        add_previous_time_in_pd_summary(pd_summary, valid_times)

        with pytest.raises(ValueError):
            self.WindForcePeriodsInitializerTester.get_term_periods(
                data_array, pd_summary, valid_times
            )

from typing import Optional

import numpy as np
import pytest

import mfire.utils.mfxarray as xr
from mfire.text.wind.reducers.gust_summary_builder import GustSummaryBuilder
from mfire.text.wind.reducers.gust_summary_builder.gust_summary_builder import GustForce
from mfire.utils.date import Datetime, Period
from tests.text.utils import generate_valid_times

from .factories import CompositeFactory1x1, CompositeFactory1x100, CompositeFactory2x2


class TestGustForce:
    @pytest.mark.parametrize(
        "force, repr_value_exp, interval_exp",
        [
            (50.0, 50, (50, 60)),
            (59.9, 50, (50, 60)),
            (60.0, 60, (60, 70)),
        ],
    )
    def test_creation(self, force, repr_value_exp, interval_exp):
        wf = GustForce(force)
        assert wf.repr_value == repr_value_exp
        assert wf.interval == interval_exp

    @pytest.mark.parametrize(
        "valid_times, data_gust, gust_force_exp",
        [
            (
                generate_valid_times(periods=1),
                np.arange(1.0, 101.0, 1, dtype=np.float64),
                GustForce(95.0),
            ),
        ],
    )
    def test_creation_from_term(self, valid_times, data_gust, gust_force_exp):
        composite = CompositeFactory1x100().get(
            valid_times=valid_times,
            data_gust=data_gust,
        )
        dataset = composite.compute()
        data_array: xr.DataArray = dataset["gust"].sel(valid_time=valid_times[0])
        gust_force: GustForce = GustForce.from_term_data_array(data_array)
        assert gust_force == gust_force_exp

    def test_comparison(self):
        assert GustForce(50) == GustForce(50)
        assert GustForce(50) <= GustForce(50)
        assert GustForce(50) >= GustForce(50)

        assert GustForce(50) == GustForce(59)

        assert GustForce(50) < GustForce(60)
        assert GustForce(60) > GustForce(50)


class TestGustSummaryBuilder:
    @pytest.mark.parametrize(
        "valid_times, data, units_compo, units_data, data_exp, unit_exp",
        [
            (
                generate_valid_times(periods=2),
                [[[0.0, 1.0], [np.nan, 20.0]], [[4.0, np.nan], [15.0, 18.0]]],
                {"gust": "km/h"},
                {"gust": "km/h"},
                [[[0.0, 1.0], [np.nan, 20.0]], [[4.0, np.nan], [15.0, 18.0]]],
                "km/h",
            ),
            (
                generate_valid_times(periods=2),
                [[[0.0, 1.0], [np.nan, 20.0]], [[4.0, np.nan], [15.0, 18.0]]],
                {"gust": "km/h"},
                {"gust": "m s**-1"},
                3.6
                * np.array(
                    [[[0.0, 1.0], [np.nan, 20.0]], [[4.0, np.nan], [15.0, 18.0]]]
                ),
                "km/h",
            ),
        ],
    )
    def test_units_conversion(
        self,
        valid_times,
        data,
        units_compo,
        units_data,
        data_exp,
        unit_exp,
    ):
        """Test the conversion of the gust unit which has to be km/h."""
        composite = CompositeFactory2x2().get(
            valid_times=valid_times,
            data_gust=data,
            units_compo=units_compo,
            units_data=units_data,
        )
        dataset = composite.compute()
        summary_builder = GustSummaryBuilder(composite, dataset)

        assert summary_builder.data.units == unit_exp

        values = summary_builder.data.sel(valid_time=valid_times).values
        np.testing.assert_allclose(values, data_exp)

    @pytest.mark.parametrize(
        "valid_times, data, gust_force_exp",
        [
            # Gusts are nan or <= 50.
            (
                generate_valid_times(periods=1),
                [[1.0, 5.0], [np.nan, 49.9]],
                None,
            ),
            # Gusts are <= 50.
            (
                generate_valid_times(periods=1),
                [[1.0, 5.0], [0.0, 49.9]],
                None,
            ),
            # All gust are <= 50.
            (
                generate_valid_times(periods=2),
                [[[1.0, 5.0], [np.nan, 49.9]], [[3.0, 25.0], [41.0, np.nan]]],
                None,
            ),
            # All gusts are nan.
            (
                generate_valid_times(periods=1),
                np.array([[np.nan, np.nan], [np.nan, np.nan]]),
                None,
            ),
            # All gusts are nan or 50.
            (
                generate_valid_times(periods=1),
                [[50.0, 50.0], [50.0, np.nan]],
                None,
            ),
            # Some gusts are > 50.
            (
                generate_valid_times(periods=1),
                [[50.0, 50.0], [50.1, np.nan]],
                GustForce(50.0),  # Q95 of [50.1]
            ),
            # Some gusts are > 50.
            (
                generate_valid_times(periods=1),
                [[50.0, 50.0], [50.1, 0.0]],
                GustForce(50.0),  # Q95 of [50.0, 50.0, 50.1]
            ),
            # Some gusts are > 50.
            (
                generate_valid_times(periods=1),
                [[50.0, 50.1], [50.2, 50.3]],
                GustForce(50.0),  # Q95 of [50.0, 50.1, 50.2, 50.3]
            ),
            # Some gusts are > 50.
            (
                generate_valid_times(periods=2),
                # > 50 -> [70., 71.], [nan, nan]
                [[[1.2, 5.3], [20.2, 20.4]], [[70.0, 71.0], [30.0, 36.0]]],
                GustForce(70.0),  # Q95 of [70., 71.]
            ),
            # Some gusts are > 50.
            (
                generate_valid_times(periods=2),
                # > 50 -> [70., 51.], [51., 51.]
                [[[51.0, 51.0], [51.0, 51.0]], [[75.0, 51.0], [51.0, 51.0]]],
                GustForce(60.0),  # Q95 of [51.0, 51.0, 51.0, 51.0, 75.0, 51.0, 51.0,
                # 51.0]
            ),
        ],
    )
    def test_gust_force_and_summary(
        self,
        valid_times,
        data: list | np.ndarray,
        gust_force_exp: Optional[float],
        assert_equals_result,
    ):
        """Test the gust summary."""
        composite = CompositeFactory2x2().get(valid_times=valid_times, data_gust=data)
        dataset = composite.compute()
        summary_builder = GustSummaryBuilder(composite, dataset)
        summary = summary_builder.compute(Datetime(2023, 1, 2, 0, 0, 0))

        # Test the gust force set in the summary_builder
        if gust_force_exp is not None:
            data_filtered: xr.DataArray = summary_builder.data.max(dim="valid_time")
            data_filtered = data_filtered.where(
                data_filtered > summary_builder.FORCE_MIN
            )
            gust_force = GustForce.from_term_data_array(data_filtered)
            assert gust_force == gust_force_exp

        # Test the summary
        assert_equals_result(summary)

    @pytest.mark.parametrize(
        "valid_times, data, periods_init_exp, periods_merged_exp",
        [
            # 000000000000: no gusts
            # - 0 init period
            # - 0 merged period
            # - 0 described period
            (
                generate_valid_times(periods=12),
                [0.0, 0.0, np.nan] * 4,
                [],
                [],
            ),
            # 000000000000: gusts are <= 50
            # - 0 init period
            # - 0 merged period
            # - 0 described period
            (
                generate_valid_times(periods=12),
                [2.0] * 12,
                [],
                [],
            ),
            # 001111111000
            # - 1 init period: 001111111000
            # - 1 merged period: 001111111000
            # - 1 described period: 001111111000
            (
                generate_valid_times(periods=12),
                [2.0] * 2 + [50.1] + [70.0] * 6 + [2.0] * 3,
                [Period(Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 8, 0, 0))],
                [Period(Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 8, 0, 0))],
            ),
            # 111111111111
            # - 1 init period: 111111111111
            # - 1 merged period: 111111111111 which cover the monitoring period
            # - 1 described period: 111111111111
            (
                generate_valid_times(periods=12),
                [70.0] * 12,
                [
                    Period(
                        Datetime(2023, 1, 1, 23, 0, 0), Datetime(2023, 1, 2, 11, 0, 0)
                    )
                ],
                [
                    Period(
                        Datetime(2023, 1, 1, 23, 0, 0), Datetime(2023, 1, 2, 11, 0, 0)
                    )
                ],
            ),
            # 001101111000:
            # - 2 init periods: 001100000000, 000001111000
            # - 1 merged period: 001111111000
            # - 1 described period: 001111111000
            (
                generate_valid_times(periods=12),
                [2.0] * 2 + [70] * 2 + [40.0] + [70] * 4 + [2.0] * 3,
                [
                    Period(
                        Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 4, 0, 0), Datetime(2023, 1, 2, 8, 0, 0)
                    ),
                ],
                [Period(Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 8, 0, 0))],
            ),
            # 001100111000:
            # - 2 init periods: 001100000000, 000000111000
            # - 1 merged period: 001111111000
            # - 1 described period: 001111111000
            (
                generate_valid_times(periods=12),
                [2.0] * 2 + [70] * 2 + [40.0] * 2 + [70] * 3 + [2.0] * 3,
                [
                    Period(
                        Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 5, 0, 0), Datetime(2023, 1, 2, 8, 0, 0)
                    ),
                ],
                [Period(Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 8, 0, 0))],
            ),
            # 001100011100:
            # - 2 init periods: 001100000000, 000000011100
            # - 1 merged period 001111111100
            # - 1 described period 001111111100
            (
                generate_valid_times(periods=12),
                [2.0] * 2 + [70] * 2 + [40.0] * 3 + [70] * 3 + [2.0] * 2,
                [
                    Period(
                        Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 6, 0, 0), Datetime(2023, 1, 2, 9, 0, 0)
                    ),
                ],
                [Period(Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 9, 0, 0))],
            ),
            # 000100011100:
            # - 2 init periods: 000100000000, 000000011100
            # - 1 merged period 000111111100
            # - 1 described period 000111111100
            (
                generate_valid_times(periods=12),
                [2.0] * 3 + [70] + [40.0] * 3 + [70] * 3 + [2.0] * 2,
                [
                    Period(
                        Datetime(2023, 1, 2, 2, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 6, 0, 0), Datetime(2023, 1, 2, 9, 0, 0)
                    ),
                ],
                [Period(Datetime(2023, 1, 2, 2, 0, 0), Datetime(2023, 1, 2, 9, 0, 0))],
            ),
            # 000100001110
            # - 2 init periods: 000100000000, 000000001110
            # - 1 merged period 0000000011100
            # - 1 described period 0000000011100
            (
                generate_valid_times(periods=12),
                [2.0] * 3 + [70] + [2.0] * 4 + [70] * 3 + [2.0],
                [
                    Period(
                        Datetime(2023, 1, 2, 2, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 7, 0, 0), Datetime(2023, 1, 2, 10, 0, 0)
                    ),
                ],
                [Period(Datetime(2023, 1, 2, 7, 0, 0), Datetime(2023, 1, 2, 10, 0, 0))],
            ),
            # 001100001110:
            # - 2 init periods: 001100000000, 000000001110
            # - 1 merged period: 000000001110
            # - 1 described period: 000000001110
            (
                generate_valid_times(periods=12),
                [2.0] * 2 + [70] * 2 + [2.0] * 4 + [70] * 3 + [2.0],
                [
                    Period(
                        Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 7, 0, 0), Datetime(2023, 1, 2, 10, 0, 0)
                    ),
                ],
                [Period(Datetime(2023, 1, 2, 7, 0, 0), Datetime(2023, 1, 2, 10, 0, 0))],
            ),
            # 011100001110:
            # - 2 init periods: 011100000000, 000000001110
            # - 2 merged periods: 011100000000 and 000000001110
            # - 2 described periods: 011100000000 and 000000001110
            (
                generate_valid_times(periods=12),
                [2.0] + [70] * 3 + [2.0] * 4 + [70] * 3 + [2.0],
                [
                    Period(
                        Datetime(2023, 1, 2, 0, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 7, 0, 0), Datetime(2023, 1, 2, 10, 0, 0)
                    ),
                ],
                [
                    Period(
                        Datetime(2023, 1, 2, 0, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 7, 0, 0), Datetime(2023, 1, 2, 10, 0, 0)
                    ),
                ],
            ),
            # 111100001111:
            # - 2 init periods: 111100000000, 000000001111
            # - 2 merged periods: 111100000000 and 000000001111
            # - 2 described periods: 111100000000 and 000000001111
            (
                generate_valid_times(periods=12),
                [70.0] * 4 + [2.0] * 4 + [70] * 4,
                [
                    Period(
                        Datetime(2023, 1, 1, 23, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 7, 0, 0), Datetime(2023, 1, 2, 11, 0, 0)
                    ),
                ],
                [
                    Period(
                        Datetime(2023, 1, 1, 23, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 7, 0, 0), Datetime(2023, 1, 2, 11, 0, 0)
                    ),
                ],
            ),
            # 001010000000
            # - 2 init periods: 001000000000, 000010000000
            # - 1 merged period: 001110000000
            # - 1 described period: 001110000000
            (
                generate_valid_times(periods=12),
                [2.0] * 2 + [70.0, 40.0, 70.0] + [2.0] * 7,
                [
                    Period(
                        Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 2, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 3, 0, 0), Datetime(2023, 1, 2, 4, 0, 0)
                    ),
                ],
                [Period(Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 4, 0, 0))],
            ),
            # 001001000000
            # - 2 init periods: 001000000000, 000001000000
            # - 1 merged period: 001111000000
            # - 1 merged described: 001111000000
            (
                generate_valid_times(periods=12),
                [2.0] * 2 + [70.0] + [40.0] * 2 + [70.0] + [2.0] * 6,
                [
                    Period(
                        Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 2, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 4, 0, 0), Datetime(2023, 1, 2, 5, 0, 0)
                    ),
                ],
                [Period(Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 5, 0, 0))],
            ),
            # 001000100000
            # - 2 init periods: 001000000000, 000000100000
            # - 1 merged period: 001111100000
            # - 1 described period: 001111100000
            (
                generate_valid_times(periods=12),
                [2.0] * 2 + [70.0] + [40.0] * 3 + [70.0] + [2.0] * 5,
                [
                    Period(
                        Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 2, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 5, 0, 0), Datetime(2023, 1, 2, 6, 0, 0)
                    ),
                ],
                [Period(Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 6, 0, 0))],
            ),
            # 001000010000
            # - 2 init periods: 001000000000, 000000010000
            # - 0 merged period
            # - 1 described period: 001000010000
            (
                generate_valid_times(periods=12),
                [2.0] * 2 + [60.0] + [40.0] * 4 + [90.0] + [2.0] * 4,
                [
                    Period(
                        Datetime(2023, 1, 2, 1, 0, 0), Datetime(2023, 1, 2, 2, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 6, 0, 0), Datetime(2023, 1, 2, 7, 0, 0)
                    ),
                ],
                [],
            ),
            # 010000000010000000000100
            # - 3 init periods: 010000000000000000000000, 000000000010000000000000,
            #  000000000000000000000100
            # - 0 merged period
            # - 0 described period
            (
                generate_valid_times(periods=24),
                [40.0, 55.0] + [40.0] * 8 + [60.0] + [40.0] * 10 + [80.0] + [40.0] * 2,
                [
                    Period(
                        Datetime(2023, 1, 2, 0, 0, 0), Datetime(2023, 1, 2, 1, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 9, 0, 0), Datetime(2023, 1, 2, 10, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 20, 0, 0), Datetime(2023, 1, 2, 21, 0, 0)
                    ),
                ],
                [],
            ),
            # 100000000001
            # - 2 init periods: 100000000000, 000000000001
            # - 0 merged period
            # - 1 described period: 100000000001
            (
                generate_valid_times(periods=12),
                [60.0] + [40.0] * 10 + [90.0],
                [
                    Period(
                        Datetime(2023, 1, 1, 23, 0, 0), Datetime(2023, 1, 2, 0, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 10, 0, 0), Datetime(2023, 1, 2, 11, 0, 0)
                    ),
                ],
                [],
            ),
            # 011100001110000111000000
            # - 3 init periods: 011100000000000000000000, 000000001110000000000000,
            # 000000000000000111000000
            # - 3 merged periods: 011100000000000000000000, 000000001110000000000000,
            # 000000000000000111000000
            # - 1 described period: 011111111111111111000000
            (
                generate_valid_times(periods=24),
                [2.0]
                + [60.0] * 3
                + [40.0] * 4
                + [70.0] * 3
                + [40.0] * 4
                + [80.0] * 3
                + [2.0] * 6,
                [
                    Period(
                        Datetime(2023, 1, 2, 0, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 7, 0, 0), Datetime(2023, 1, 2, 10, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 14, 0, 0), Datetime(2023, 1, 2, 17, 0, 0)
                    ),
                ],
                [
                    Period(
                        Datetime(2023, 1, 2, 0, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 7, 0, 0), Datetime(2023, 1, 2, 10, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 14, 0, 0), Datetime(2023, 1, 2, 17, 0, 0)
                    ),
                ],
            ),
            # 011100001110000111000010
            # - 4 init periods: 011100000000000000000000, 000000001110000000000000,
            # 000000000000000111000000, 000000000000000000000010
            # - 3 merged periods: 011100000000000000000000, 000000001110000000000000,
            # 000000000000000111000000
            # - 1 described period: 011111111111111111000000
            (
                generate_valid_times(periods=24),
                [2.0]
                + [60.0] * 3
                + [40.0] * 4
                + [70.0] * 3
                + [40.0] * 4
                + [80.0] * 3
                + [2.0] * 4
                + [90.0, 2.0],
                [
                    Period(
                        Datetime(2023, 1, 2, 0, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 7, 0, 0), Datetime(2023, 1, 2, 10, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 14, 0, 0), Datetime(2023, 1, 2, 17, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 21, 0, 0), Datetime(2023, 1, 2, 22, 0, 0)
                    ),
                ],
                [
                    Period(
                        Datetime(2023, 1, 2, 0, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 7, 0, 0), Datetime(2023, 1, 2, 10, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 14, 0, 0), Datetime(2023, 1, 2, 17, 0, 0)
                    ),
                ],
            ),
            # 111100001110000111111111
            # - 3 init periods: 111100000000000000000000, 000000001110000000000000,
            # 000000000000000111111111
            # - 3 merged periods: 111100000000000000000000, 000000001110000000000000,
            # 000000000000000111111111
            # - 1 described period: 111111111111111111111111
            (
                generate_valid_times(periods=24),
                [60.0] * 4 + [40.0] * 4 + [70.0] * 3 + [40.0] * 4 + [80.0] * 9,
                [
                    Period(
                        Datetime(2023, 1, 1, 23, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 7, 0, 0), Datetime(2023, 1, 2, 10, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 14, 0, 0), Datetime(2023, 1, 2, 23, 0, 0)
                    ),
                ],
                [
                    Period(
                        Datetime(2023, 1, 1, 23, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 7, 0, 0), Datetime(2023, 1, 2, 10, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 14, 0, 0), Datetime(2023, 1, 2, 23, 0, 0)
                    ),
                ],
            ),
            # 111100011110011100001110:
            # - 4 init periods: 111100000000000000000000, 000000011110000000000000,
            # 000000000000011100000000, 000000000000000000001110
            # - 2 merged period 111111111111111100001110
            # - 2 described period 111111111111111100001110
            (
                generate_valid_times(periods=24),
                [60] * 4
                + [40] * 3
                + [70] * 4
                + [40.0] * 2
                + [90] * 3
                + [40] * 4
                + [80.0] * 3
                + [2],
                [
                    Period(
                        Datetime(2023, 1, 1, 23, 0, 0), Datetime(2023, 1, 2, 3, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 6, 0, 0), Datetime(2023, 1, 2, 10, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 12, 0, 0), Datetime(2023, 1, 2, 15, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 19, 0, 0), Datetime(2023, 1, 2, 22, 0, 0)
                    ),
                ],
                [
                    Period(
                        Datetime(2023, 1, 1, 23, 0, 0), Datetime(2023, 1, 2, 15, 0, 0)
                    ),
                    Period(
                        Datetime(2023, 1, 2, 19, 0, 0), Datetime(2023, 1, 2, 22, 0, 0)
                    ),
                ],
            ),
        ],
    )
    def test_gust_periods_and_summary(
        self,
        valid_times,
        data: np.ndarray,
        periods_init_exp: list[Period],
        periods_merged_exp: list[Period],
        assert_equals_result,
    ):
        """Test the gust summary."""
        composite = CompositeFactory1x1().get_composite_when_term_data_is_one_number(
            valid_times=valid_times, data_gust=data
        )

        dataset = composite.compute()
        summary_builder = GustSummaryBuilder(composite, dataset)

        # Generate the gust summary
        summary = summary_builder.compute(Datetime(2023, 1, 2, 0, 0, 0))

        # Check periods_init
        periods_init: list[Period] = summary_builder._get_initial_gust_periods()
        assert periods_init == periods_init_exp

        # Check periods_merged
        periods_merged: list[Period] = summary_builder._merge_gust_periods(periods_init)
        assert periods_merged == periods_merged_exp

        # Check text
        assert_equals_result(summary)

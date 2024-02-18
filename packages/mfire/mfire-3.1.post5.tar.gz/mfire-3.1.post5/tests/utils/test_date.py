"""test_datetime.py

Unit tests of the utils.date module.
"""
# Build in libraries
from datetime import datetime, timedelta, timezone

import numpy as np

# Third parties packages
import pytest

import mfire.utils.mfxarray as xr

# Own package
from mfire.utils.date import LOCAL_TIMEZONE, Datetime, Period, Periods, Timedelta
from tests.functions_test import assert_identically_close

# numpy.random seed
np.random.seed(42)


class TestPeriods:
    def test_properties(self):
        periods = Periods(
            [
                Period(Datetime(2021, 1, 1, 5), Datetime(2021, 1, 1, 8)),
                Period(Datetime(2021, 1, 1, 12), Datetime(2021, 1, 1, 15)),
            ]
        )
        assert periods.begin_time == Datetime(2021, 1, 1, 5)
        assert periods.end_time == Datetime(2021, 1, 1, 15)

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (
                [
                    Period(Datetime(2021, 1, 1, 5), Datetime(2021, 1, 1, 8)),
                ],
                [],
                [
                    Period(Datetime(2021, 1, 1, 5), Datetime(2021, 1, 1, 8)),
                ],
            ),
            (
                [],
                [
                    Period(Datetime(2021, 1, 1, 5), Datetime(2021, 1, 1, 8)),
                ],
                [
                    Period(Datetime(2021, 1, 1, 5), Datetime(2021, 1, 1, 8)),
                ],
            ),
            (
                [
                    Period(Datetime(2021, 1, 1, 5), Datetime(2021, 1, 1, 8)),
                    Period(Datetime(2021, 1, 1, 12), Datetime(2021, 1, 1, 15)),
                ],
                [
                    Period(Datetime(2021, 1, 1, 6), Datetime(2021, 1, 1, 9)),
                    Period(Datetime(2021, 1, 1, 10), Datetime(2021, 1, 1, 11)),
                    Period(Datetime(2021, 1, 1, 14), Datetime(2021, 1, 1, 19)),
                ],
                [
                    Period(Datetime(2021, 1, 1, 5), Datetime(2021, 1, 1, 9)),
                    Period(Datetime(2021, 1, 1, 10), Datetime(2021, 1, 1, 11)),
                    Period(Datetime(2021, 1, 1, 12), Datetime(2021, 1, 1, 19)),
                ],
            ),
        ],
    )
    def test_add(self, a, b, expected):
        assert Periods(a) + Periods(b) == Periods(expected)

        p = Periods(a)
        p += Periods(b)
        assert p == Periods(expected)

    @pytest.mark.parametrize(
        "dates,expected",
        [
            # Union of two datetimes without covering
            (
                [
                    Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 6)),
                    Period(Datetime(2023, 3, 4, 8), Datetime(2023, 3, 4, 12)),
                ],
                [
                    Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 6)),
                    Period(Datetime(2023, 3, 4, 8), Datetime(2023, 3, 4, 12)),
                ],
            ),
            # Union of two datetimes with covering
            (
                [
                    Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 10)),
                    Period(Datetime(2023, 3, 4, 8), Datetime(2023, 3, 4, 12)),
                ],
                [Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 12))],
            ),
            # Union of two datetimes unsorted
            (
                [
                    Period(Datetime(2023, 3, 4, 8), Datetime(2023, 3, 4, 12)),
                    Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 10)),
                ],
                [Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 12))],
            ),
            # Repetition of two datetimes
            (
                [
                    Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 10)),
                    Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 10)),
                ],
                [Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 10))],
            ),
        ],
    )
    def test_reduce_without_n(self, dates, expected):
        periods = Periods(dates)
        assert periods.reduce() == Periods(expected)

    @pytest.mark.parametrize(
        "dates,expected",
        [
            # Reduce the two first
            (
                [
                    Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 10)),
                    Period(Datetime(2023, 3, 4, 11), Datetime(2023, 3, 4, 13)),
                    Period(Datetime(2023, 3, 4, 19), Datetime(2023, 3, 4, 20)),
                ],
                [
                    Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 13)),
                    Period(Datetime(2023, 3, 4, 19), Datetime(2023, 3, 4, 20)),
                ],
            ),
            # Reduce the two last
            (
                [
                    Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 10)),
                    Period(Datetime(2023, 3, 4, 15), Datetime(2023, 3, 4, 18)),
                    Period(Datetime(2023, 3, 4, 19), Datetime(2023, 3, 4, 20)),
                ],
                [
                    Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 10)),
                    Period(Datetime(2023, 3, 4, 15), Datetime(2023, 3, 4, 20)),
                ],
            ),
            # Reduce the third first
            (
                [
                    Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 8)),
                    Period(Datetime(2023, 3, 4, 11), Datetime(2023, 3, 4, 13)),
                    Period(Datetime(2023, 3, 4, 14), Datetime(2023, 3, 4, 15)),
                    Period(Datetime(2023, 3, 4, 22), Datetime(2023, 3, 4, 23)),
                ],
                [
                    Period(Datetime(2023, 3, 4, 4), Datetime(2023, 3, 4, 15)),
                    Period(Datetime(2023, 3, 4, 22), Datetime(2023, 3, 4, 23)),
                ],
            ),
        ],
    )
    def test_reduce_with_n(self, dates, expected):
        periods = Periods(dates)
        assert periods.reduce(n=2) == Periods(expected)

    @pytest.mark.parametrize(
        "periods,expected",
        [
            (
                [
                    Period(Datetime(2021, 1, 1, 5), Datetime(2021, 1, 1, 8)),
                    Period(Datetime(2021, 1, 1, 11), Datetime(2021, 1, 1, 15)),
                ],
                7,
            ),
            (
                [
                    Period(Datetime(2021, 1, 1, 5), Datetime(2021, 1, 2, 8)),
                    Period(Datetime(2021, 1, 2, 11), Datetime(2021, 1, 2, 15)),
                ],
                31,
            ),
        ],
    )
    def test_total_hours(self, periods, expected):
        assert Periods(periods).total_hours == expected

    @pytest.mark.parametrize(
        "periods,expected",
        [
            (
                [],
                0,
            ),
            (
                [
                    Period(Datetime(2021, 1, 1, 5), Datetime(2021, 1, 1, 8)),
                    Period(Datetime(2021, 1, 1, 11), Datetime(2021, 1, 1, 15)),
                ],
                1,
            ),
            (
                [
                    Period(Datetime(2021, 1, 1, 5), Datetime(2021, 1, 2, 8)),
                    Period(Datetime(2021, 1, 2, 11), Datetime(2021, 1, 2, 15)),
                ],
                2,
            ),
        ],
    )
    def test_total_days(self, periods, expected):
        assert Periods(periods).total_days == expected

    def test_all_intersections(self):
        p1 = Periods(
            [
                Period(Datetime(2023, 3, 1, 5), Datetime(2023, 3, 1, 10)),
                Period(Datetime(2023, 3, 1, 16), Datetime(2023, 3, 1, 19)),
            ]
        )
        p2 = Periods(
            [
                Period(Datetime(2023, 3, 1, 8), Datetime(2023, 3, 1, 12)),
                Period(Datetime(2023, 3, 1, 15), Datetime(2023, 3, 1, 20)),
            ]
        )

        assert list(p1.all_intersections(p2)) == [
            Timedelta(hours=2),
            Timedelta(hours=3),
        ]

    def test_hours_of_intersection(self):
        p1 = Periods(
            [
                Period(Datetime(2023, 3, 1, 5), Datetime(2023, 3, 1, 10)),
                Period(Datetime(2023, 3, 1, 16), Datetime(2023, 3, 1, 19)),
            ]
        )
        p2 = Periods(
            [
                Period(Datetime(2023, 3, 1, 8), Datetime(2023, 3, 1, 12)),
                Period(Datetime(2023, 3, 1, 15), Datetime(2023, 3, 1, 20)),
            ]
        )

        assert p1.hours_of_intersection(p2) == 5

    def test_hours_of_union(self):
        p1 = Periods(
            [
                Period(Datetime(2023, 3, 1, 5), Datetime(2023, 3, 1, 10)),
                Period(Datetime(2023, 3, 1, 16), Datetime(2023, 3, 1, 19)),
            ]
        )
        p2 = Periods(
            [
                Period(Datetime(2023, 3, 1, 8), Datetime(2023, 3, 1, 12)),
                Period(Datetime(2023, 3, 1, 15), Datetime(2023, 3, 1, 20)),
            ]
        )

        assert p1.hours_of_union(p2) == 12

    def test_are_same_temporalities(self):
        p1 = Periods(
            [
                Period(Datetime(2023, 3, 1, 5), Datetime(2023, 3, 1, 10)),
            ]
        )
        p2 = Periods(
            [
                Period(Datetime(2023, 3, 1, 6), Datetime(2023, 3, 1, 12)),
            ]
        )
        p3 = Periods(
            [
                Period(Datetime(2023, 3, 1, 15), Datetime(2023, 3, 1, 20)),
            ]
        )
        assert p1.are_same_temporalities(p2) is True
        assert p1.are_same_temporalities(p3) is False
        assert p1.are_same_temporalities(p2, p3) is False

        # the proportion of overlap is less than 25%
        p3 = Periods(
            [
                Period(Datetime(2023, 1, 1), Datetime(2024, 1, 1)),
            ]
        )
        p4 = Periods(
            [
                Period(Datetime(2022, 1, 1), Datetime(2023, 1, 2)),
            ]
        )
        assert p3.are_same_temporalities(p4) is False


class TestPeriod:

    _p1 = Period(Datetime(2021, 1, 1), Datetime(2021, 1, 2))
    _p2 = Period(Datetime(2021, 1, 3), Datetime(2021, 1, 4))
    _p3 = Period(Datetime(2021, 1, 1, 23), Datetime(2021, 1, 2, 23))
    _p4 = Period(Datetime(2021, 1, 1, 10), Datetime(2021, 1, 1, 12))
    _p5 = Period(Datetime(2021, 1, 1, 11), Datetime(2021, 1, 1, 15))
    _p6 = Period(Datetime(2021, 1, 1, 12), Datetime(2021, 1, 1, 16))

    _d1 = Datetime(2021, 1, 1, 20)
    _d2 = Datetime(2021, 1, 2, 12)
    _d3 = Datetime(2021, 1, 5, 9)
    _d4 = Datetime(2021, 2, 1, 9)
    _d5 = Datetime(2021, 1, 1, 18)

    def test_init(self):
        assert isinstance(self._p1, Period)
        assert isinstance(Period(Datetime(2021, 4, 17)), Period)
        assert isinstance(Period("20210417"), Period)

        assert hash(self._p1) == -7293705823702154491
        assert self._p1.to_json == {
            "begin_time": Datetime(2021, 1, 1),
            "end_time": Datetime(2021, 1, 2),
        }
        assert (
            str(self._p1) == "Period(begin_time=2021-01-01T00:00:00+00:00, "
            "end_time=2021-01-02T00:00:00+00:00)"
        )

    @pytest.mark.parametrize(
        "period,begin_time,expected",
        [
            (_p2, _d1, Period(_d1, Datetime(2021, 1, 4))),
            (_p2, _d3, Period(_d3, _d3)),
            (Period(_d1, _d1), _d3, Period(_d3, _d3)),
        ],
    )
    def test_set_begin_time(self, period, begin_time, expected):
        period = period.copy()
        period.begin_time = begin_time
        assert period == expected

    @pytest.mark.parametrize(
        "period,end_time,expected",
        [
            (_p2, _d1, Period(_d1, _d1)),
            (_p2, _d3, Period(Datetime(2021, 1, 3), _d3)),
            (Period(_d3, _d3), _d1, Period(_d1, _d1)),
            (Period(_d1, _d3), None, Period(_d1, _d1)),
        ],
    )
    def test_set_end_time(self, period, end_time, expected):
        period = period.copy()
        period.end_time = end_time
        assert period == expected

    @pytest.mark.parametrize(
        "p1,p2,expected",
        [
            (_p1, _p2, Period("20210101", "20210104")),
            (_p2, _p1, Period("20210101", "20210104")),
            (_p1, _p3, Period("20210101", "202101022300")),
            (_p2, _p3, Period("202101012300", "20210104")),
        ],
    )
    def test_basic_union(self, p1, p2, expected):
        assert p1.basic_union(p2) == expected

    @pytest.mark.parametrize(
        "p1,p2,expected",
        [
            (_p1, _p2, Periods([_p1, _p2])),
            (_p2, _p1, Periods([_p1, _p2])),
            (
                _p4,
                _p5,
                Periods([Period(Datetime(2021, 1, 1, 10), Datetime(2021, 1, 1, 15))]),
            ),
            (
                _p4,
                _p6,
                Periods([Period(Datetime(2021, 1, 1, 10), Datetime(2021, 1, 1, 16))]),
            ),
        ],
    )
    def test_union(self, p1, p2, expected):
        assert p1.union(p2) == expected

    @pytest.mark.parametrize(
        "p1,p2,expected",
        [
            (_p1, _p2, False),
            (_p1, _p3, True),
            (_p2, _p3, True),
        ],
    )
    def test_extends(self, p1, p2, expected):
        assert p1.extends(p2) is expected

    @pytest.mark.parametrize(
        "p1,p2,expected",
        [
            (_p1, _p2, False),
            (_p1, _p3, True),
            (_p2, _p3, False),
        ],
    )
    def test_intersects(self, p1, p2, expected):
        assert p1.intersects(p2) is expected

    @pytest.mark.parametrize(
        "p1,p2,expected",
        [
            (_p4, _p5, Timedelta(hours=1)),
            (_p4, _p2, Timedelta(hours=0)),
            (_p5, _p6, Timedelta(hours=3)),
        ],
    )
    def test_intersection(self, p1, p2, expected):
        assert p1.intersection(p2) == expected

    @pytest.mark.parametrize(
        "begin_time,end_time,expected",
        [
            (_d5, _d1, "ce vendredi en soirée"),
            (_d5, _d2, "de ce vendredi soir à samedi mi-journée"),
            (_d5, _d3, "de ce soir jusqu'à mardi matin"),
            (_d5, _d4, "de ce soir jusqu'à lundi 1er février dans la matinée"),
        ],
    )
    def test_describe(self, begin_time, end_time, expected):
        request_time = Datetime(2021, 1, 1, 12)
        assert Period(begin_time, end_time).describe(request_time) == expected


class TestDatetime:
    def test_init(self):
        dates = [
            Datetime(2021, 4, 17),
            Datetime(year=2021, month=4, day=17),
            Datetime("20210417"),
            Datetime("20210417T000000"),
            Datetime("2021-04-17 00:00:00"),
            Datetime("2021-04-17T00:00:00+00:00"),
            Datetime("2021-04-17T00:00:00Z"),
            Datetime(b"\x07\xe5\x04\x11\x00\x00\x00\x00\x00\x00"),
            Datetime(datetime(2021, 4, 17)),
            Datetime(1618617600.0),
            Datetime("2021-04-17T01:00:00+01:00"),
            Datetime(2021, 4, 17, 1, tzinfo=timezone(timedelta(hours=1))),
            Datetime(
                b"\x07\xe5\x04\x11\x01\x00\x00\x00\x00\x00",
                tzinfo=timezone(timedelta(hours=1)),
            ),
            Datetime(xr.DataArray(datetime(2021, 4, 17))),
        ]
        assert all(isinstance(d, Datetime) for d in dates)
        assert all(d == dates[0] for d in dates)

        with pytest.raises(ValueError, match="Datetime value unknown"):
            Datetime(set())

    def test_properties(self):
        d0 = Datetime(2021, 12, 21, 18, 44, 56)
        assert d0.rounded == Datetime(2021, 12, 21, 18)
        assert d0.midnight == Datetime(2021, 12, 21)
        assert str(d0) == "2021-12-21T18:44:56+00:00"
        assert d0.as_datetime == datetime(2021, 12, 21, 18, 44, 56, tzinfo=timezone.utc)
        assert d0.is_synoptic()
        assert d0.weekday_name == "mardi"
        assert d0.month_name == "décembre"
        assert d0.literal_day() == "mardi 21 décembre 2021"
        assert d0.moment.get("name") == "soir"
        assert d0.calendar_date == Datetime(2021, 12, 21)

    def test_is_same_day(self):
        d0 = Datetime(2021, 12, 21, 18, 44, 56)
        d1 = Datetime(2021, 12, 22, 18, 44, 56)
        d2 = Datetime(2021, 12, 21, 20, 44, 56)

        assert not d0.is_same_day(d1)
        assert not d1.is_same_day(d2)
        assert d0.is_same_day(d2)

    def test_describe(self):
        d0 = Datetime(2021, 12, 21, 18, 44, 56)
        d1 = Datetime(2021, 12, 20, 18)
        d2 = Datetime(2021, 12, 14, 23)
        d3 = Datetime(2021, 12, 22, 1)

        assert d0.describe_day(d0) == "aujourd'hui"
        assert d0.describe_day(d1) == "demain"
        assert d0.describe_day(d2) == "mardi prochain"
        assert d0.describe_moment(d0) == "ce soir"
        assert d0.describe_moment(d1) == "soir"
        assert d0.describe(d0) == "ce soir"
        assert d0.describe(d1) == "demain soir"
        assert d0.describe(d2) == "mardi prochain dans la soirée"
        assert d2.describe(d1) == "la nuit de mardi dernier à mercredi dernier"
        assert d3.describe(d0) == "cette nuit"
        assert d3.describe(d1) == "la nuit de demain à mercredi"
        assert d3.describe(d3) == "cette nuit"

    def test_describe_as_period(self):
        d0 = Datetime(2023, 3, 1, 6)
        d1 = Datetime(2323, 3, 1, 15)
        assert d1.describe_as_period(d0) == "jeudi après-midi"

    def test_timezone(self):
        assert Datetime().tzinfo == timezone.utc
        assert Datetime(2021, 1, 1).tzinfo == timezone.utc
        assert Datetime.now().tzinfo == LOCAL_TIMEZONE
        assert Datetime(2021, 1, 1) == Datetime(2021, 1, 1, tzinfo=timezone.utc)
        d0 = Datetime(2021, 1, 1, 1, tzinfo=timezone(timedelta(hours=1)))
        assert d0 == Datetime(2021, 1, 1)
        assert d0.utc == d0

    def test_xarray_sel(self):
        # tests data arrays
        da0 = xr.DataArray(
            np.arange(24),
            dims=("valid_time"),
            coords={
                "valid_time": [Datetime(2021, 1, 1, i).as_np_dt64 for i in range(24)]
            },
        )
        vals = [6, 8, 1, 9, 12]
        da1 = da0.isel(valid_time=15)
        da2 = da0.isel(valid_time=vals)
        da3 = da0.isel(valid_time=slice(vals[0], vals[-1]))

        # selection using utc Datetimes
        dt_list = [Datetime(2021, 1, 1, i) for i in vals]
        assert_identically_close(
            da1, da0.sel(valid_time=Datetime(2021, 1, 1, 15).without_tzinfo)
        )
        assert_identically_close(
            da2, da0.sel(valid_time=[dt.as_np_dt64 for dt in dt_list])
        )
        assert_identically_close(
            da3,
            da0.sel(
                valid_time=slice(
                    dt_list[0].without_tzinfo,
                    (dt_list[-1] - Timedelta(hours=1)).without_tzinfo,
                )
            ),
        )
        assert_identically_close(
            da3,
            da0.sel(
                valid_time=slice(
                    dt_list[0].as_np_dt64,
                    (dt_list[-1] - Timedelta(microseconds=1)).as_np_dt64,
                )
            ),
        )  # cas où une borne du slice n'est pas dans l'index : besoin de comparer
        # entre tz-naive et aware si on utilise pas des np_datetime64

        # selection using local Datetimes
        for shift in (4, 1, 2, 6, -1, -2, -8):
            local_delta = timedelta(hours=shift)
            local_tz = timezone(local_delta)
            local_dt_list = [
                Datetime(2021, 1, 1, i, tzinfo=local_tz) + local_delta for i in vals
            ]
            local_dt = Datetime(2021, 1, 1, 15, tzinfo=local_tz) + local_delta
            assert_identically_close(da1, da0.sel(valid_time=local_dt.without_tzinfo))
            assert_identically_close(
                da2, da0.sel(valid_time=[dt.as_np_dt64 for dt in local_dt_list])
            )
            assert_identically_close(
                da3,
                da0.sel(
                    valid_time=slice(
                        local_dt_list[0].without_tzinfo,
                        (local_dt_list[-1] - Timedelta(hours=1)).without_tzinfo,
                    )
                ),
            )
            assert_identically_close(
                da3,
                da0.sel(
                    valid_time=slice(
                        local_dt_list[0].as_np_dt64,
                        (local_dt_list[-1] - Timedelta(microseconds=1)).as_np_dt64,
                    )
                ),
            )  # cas où une borne du slice n'est pas dans l'index : besoin de comparer
            # entre tz-naive et aware si on utilise pas des np_datetime64

    def test_format_bracket_str(self):
        d0 = Datetime(2023, 3, 1, 5)
        assert d0.format_bracket_str("[date+3]") == "2023-03-04T00:00:00+00:00"
        assert d0.format_bracket_str(3) == 3


class TestTimedelta:
    def test_init(self):
        assert isinstance(Timedelta(1, 2, 3), Timedelta)
        assert Timedelta(1) == Timedelta(days=1)
        assert Timedelta(1, 2) == Timedelta(days=1, seconds=2)
        assert Timedelta(1, 2, 3) == Timedelta(days=1, seconds=2, microseconds=3)
        assert isinstance(Timedelta(hours=1), Timedelta)
        assert isinstance(Timedelta(timedelta(days=1)), Timedelta)

        with pytest.raises(ValueError, match="No initial value provided for Timedelta"):
            Timedelta()

    def test_operations(self):
        # Additions
        #   Datetime & Datetime
        assert isinstance(Timedelta(hours=-1) + Datetime(2021, 1, 1), Datetime)
        with pytest.raises(TypeError):
            print(Datetime(2021, 1, 1, 1) + Datetime(2021, 1, 1))
        #   Datetime & Timedelta
        assert Datetime(2021, 1, 1) + Timedelta(hours=1) == Datetime(2021, 1, 1, 1)
        assert isinstance(Datetime(2021, 1, 1) + Timedelta(hours=1), Datetime)
        assert Datetime(2021, 1, 1) + Timedelta(hours=-1) == Datetime(2020, 12, 31, 23)
        assert isinstance(Datetime(2021, 1, 1) + Timedelta(hours=-1), Datetime)
        assert Timedelta(hours=1) + Datetime(2021, 1, 1) == Datetime(2021, 1, 1, 1)
        assert isinstance(Timedelta(hours=1) + Datetime(2021, 1, 1), Datetime)
        assert Timedelta(hours=-1) + Datetime(2021, 1, 1) == Datetime(2020, 12, 31, 23)
        assert Datetime(2021, 1, 1) + timedelta(hours=1) == Datetime(2021, 1, 1, 1)
        assert isinstance(Datetime(2021, 1, 1) + timedelta(hours=1), Datetime)
        # TO DO : assert datetime(2021,1,1)+Timedelta(hours=1)==Datetime(2021,1,1,1)
        # TO DO : assert isinstance(datetime(2021, 1, 1) + Timedelta(hours=1), Datetime)
        assert timedelta(hours=1) + Datetime(2021, 1, 1) == Datetime(2021, 1, 1, 1)
        assert isinstance(timedelta(hours=1) + Datetime(2021, 1, 1), Datetime)
        # TO DO : assert Timedelta(hours=-1)+datetime(2021,1,1)==Datetime(2020,12,31,23)
        # TO DO :assert isinstance(Timedelta(hours=-1) + datetime(2021, 1, 1), Datetime)
        #   Datetime & {int, float, str}
        with pytest.raises(TypeError):
            print(Datetime.now() + 1)
        with pytest.raises(TypeError):
            print(Datetime.now() + 3.14)
        with pytest.raises(TypeError):
            print(Datetime.now() + "toto")

        #   Timedelta & Timedelta
        assert Timedelta(hours=1) + Timedelta(days=1) == Timedelta(days=1, hours=1)
        assert isinstance(Timedelta(hours=1) + Timedelta(days=1), Timedelta)
        assert Timedelta(hours=1) + timedelta(hours=1) == Timedelta(hours=2)
        assert isinstance(Timedelta(hours=1) + timedelta(hours=1), Timedelta)
        #   Timedelta & {int, float, str}
        with pytest.raises(TypeError):
            print(Timedelta(1) + 1)
        with pytest.raises(TypeError):
            print(Timedelta(1) + 3.14)
        with pytest.raises(TypeError):
            print(Timedelta(1) + "toto")

        # subtractions
        #   Datetime & Datetime
        assert Datetime(2021, 1, 1, 1) - Datetime(2021, 1, 1) == Timedelta(hours=1)
        assert isinstance(Datetime(2021, 1, 1, 1) - Datetime(2021, 1, 1), Timedelta)
        assert Datetime(2021, 1, 1) - Datetime(2021, 1, 1, 1) == Timedelta(hours=-1)
        assert isinstance(Datetime(2021, 1, 1) - Datetime(2021, 1, 1, 1), Timedelta)
        with pytest.raises(TypeError):
            print(Datetime(2021, 1, 1, 1) - datetime(2021, 1, 1))
        with pytest.raises(TypeError):
            datetime(2021, 1, 1) - Datetime(2021, 1, 1, 1) == Timedelta(hours=-1)
        #   Datetime & Timedelta
        assert Datetime(2021, 1, 1, 1) - Timedelta(hours=1) == Datetime(2021, 1, 1)
        assert isinstance(Datetime(2021, 1, 1, 1) - Timedelta(hours=1), Datetime)
        assert Datetime(2021, 1, 1, 1) - timedelta(hours=1) == Datetime(2021, 1, 1)
        assert isinstance(Datetime(2021, 1, 1, 1) - timedelta(hours=1), Datetime)
        # TO DO : assert datetime(2021,1,1,1)-Timedelta(hours=1)==Datetime(2021,1,1)
        # TO DO : assert isinstance(datetime(2021,1,1,1)-Timedelta(hours=1),Datetime)
        assert Datetime(2021, 1, 1) - Timedelta(hours=-1) == Datetime(2021, 1, 1, 1)
        with pytest.raises(TypeError):
            print(Timedelta(1) - Datetime.now())
        #   Datetime & {int, float, str}
        with pytest.raises(TypeError):
            print(Datetime.now() - 1)
        with pytest.raises(TypeError):
            print(Datetime.now() - 3.14)
        with pytest.raises(TypeError):
            print(Datetime.now() - "toto")
        #   Timedelta & Timedelta
        assert Timedelta(-1) == -Timedelta(1)
        assert isinstance(-Timedelta(1), Timedelta)
        assert Timedelta(1) - Timedelta(hours=1) == Timedelta(hours=23)
        assert isinstance(Timedelta(1) - Timedelta(hours=1), Timedelta)
        assert Timedelta(hours=1) - Timedelta(1) == Timedelta(hours=-23)
        assert isinstance(Timedelta(hours=1) - Timedelta(1), Timedelta)
        assert Timedelta(1) - timedelta(hours=1) == Timedelta(hours=23)
        assert isinstance(Timedelta(1) - timedelta(hours=1), Timedelta)
        assert timedelta(1) - Timedelta(hours=1) == Timedelta(hours=23)
        assert isinstance(timedelta(1) - Timedelta(hours=1), Timedelta)
        #   Timedelta & {int, float, str}
        with pytest.raises(TypeError):
            print(Timedelta(1) - 1)
        with pytest.raises(TypeError):
            print(Timedelta(1) - 3.14)
        with pytest.raises(TypeError):
            print(Timedelta(1) - "toto")

        # Multiplications
        #   Timedelta & {int, float}
        assert 42 * Timedelta(1) == Timedelta(42) == Timedelta(1) * 42
        assert (
            3.14 * Timedelta(1) == Timedelta(3.14) == Timedelta(days=3, seconds=12096)
        )
        assert (
            Timedelta(1) * 3.14 == Timedelta(3.14) == Timedelta(days=3, seconds=12096)
        )
        assert isinstance(42 * Timedelta(1), Timedelta)
        assert isinstance(3.14 * Timedelta(1), Timedelta)
        assert isinstance(Timedelta(1) * 42, Timedelta)
        assert isinstance(Timedelta(1) * 3.14, Timedelta)

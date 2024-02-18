import numpy as np

from mfire.localisation.altitude import AltitudeInterval, Segment, rename_alt_min_max


class TestAltitudeFunctions:
    def test_rename_alt_min_max(self):
        assert rename_alt_min_max("à Toulouse") == "à Toulouse"
        assert rename_alt_min_max("entre 1000 m et 2000 m", alt_max=2000)


class TestSegment:
    def test_init(self):
        assert Segment(2, 3) == (2, 3)
        assert Segment(np.nan, 5) == (-np.inf, +np.inf)
        assert Segment(5, np.nan) == (-np.inf, +np.inf)


class TestAltitudeInterval:
    def test_operators(self):
        assert -AltitudeInterval((-3, 5)) == AltitudeInterval((3, -5))

        assert AltitudeInterval((-5, 5)) in AltitudeInterval((-10, 10))
        assert AltitudeInterval((-5, 15)) not in AltitudeInterval((-10, 10))

        assert str(AltitudeInterval((-3, 5))) == "AltitudeInterval([-3, 5])"

    def test_inversion(self):
        assert ~AltitudeInterval([-np.inf, 0]) == AltitudeInterval([0, np.inf])
        assert ~AltitudeInterval([0, 100]) == AltitudeInterval(
            [-np.inf, 0], [100, np.inf]
        )
        assert ~AltitudeInterval([0]) == AltitudeInterval([-np.inf, np.inf])
        assert ~AltitudeInterval(
            [-np.inf, 0], [100, 200], [300], [400, np.inf]
        ) == AltitudeInterval([0, 100], [200, 400])

    def test_difference(self):
        assert AltitudeInterval([0, 1000]).difference(
            [500, np.inf]
        ) == AltitudeInterval([0, 500])

    def test_symmetric_difference(self):
        assert AltitudeInterval([0, 1000]).symmetric_difference(
            [500, np.inf]
        ) == AltitudeInterval([0, 500], [1000, np.inf])

    def test_is_sub_interval(self):
        my_interval = AltitudeInterval([0, 1000])
        assert my_interval.is_sub_interval((0, 2000)) is True
        assert my_interval.is_sub_interval((500, 2000)) is False

    def test_is_super_interval(self):
        my_interval = AltitudeInterval((0, 1000))
        assert my_interval.is_super_interval((0, 500)) is True
        assert my_interval.is_super_interval((-100, 500)) is False

    def test_name_segment(self):
        assert AltitudeInterval.name_segment((-np.inf, 1000)) == "en dessous de 1000 m"
        assert AltitudeInterval.name_segment((1000, np.inf)) == "au-dessus de 1000 m"
        assert AltitudeInterval.name_segment((1000, 2000)) == "entre 1000 m et 2000 m"
        assert (
            AltitudeInterval.name_segment((1000, 2000), alt_max=2000)
            == "au-dessus de 1000 m"
        )
        assert AltitudeInterval.name_segment((1000, 1000)) == "à 1000 m"
        assert AltitudeInterval.name_segment((0, 1000), alt_min=0, alt_max=800) == ""
        assert AltitudeInterval.name_segment((1000, 1000), alt_min=1000) == ""
        assert AltitudeInterval.name_segment((1500, 1000)) == ""

    def test_name(self):
        empty = AltitudeInterval()
        assert empty.name() == ""

        inter = AltitudeInterval((-np.inf, 100), (200, 300), (400), (500, 1000))
        assert (
            inter.name()
            == "en dessous de 100 m, entre 200 m et 300 m, à 400 m et entre 500 m et "
            "1000 m"
        )
        assert (
            inter.name(alt_max=1000)
            == "en dessous de 100 m, entre 200 m et 300 m, à 400 m et au-dessus de "
            "500 m"
        )
        assert inter.name(alt_min=400, alt_max=800) == "au-dessus de 500 m"

    def test_from_str(self):
        assert AltitudeInterval.from_str("au-dessus de 800 m") == AltitudeInterval(
            [800.0, np.inf]
        )
        assert AltitudeInterval.from_str("entre 1000 m et 2000 m") == AltitudeInterval(
            [1000.0, 2000.0]
        )
        assert AltitudeInterval.from_str("à 200 m") == AltitudeInterval([200.0, 200.0])
        assert AltitudeInterval.from_str("en dessous de 450 m") == AltitudeInterval(
            [-np.inf, 450]
        )
        assert AltitudeInterval.from_str(
            "en dessous de 100 m, entre 800 m et 900 m et au-dessus de 1000 m"
        ) == AltitudeInterval([-np.inf, 100], [800, 900], [1000, np.inf])
        assert AltitudeInterval.from_str("à Toulouse") == AltitudeInterval()

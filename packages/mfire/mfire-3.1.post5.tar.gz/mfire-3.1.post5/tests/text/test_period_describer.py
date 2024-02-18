from mfire.text.period_describer import PeriodDescriber
from mfire.utils.date import Datetime, Period, Periods


class TestPeriodDescriber:
    def test_period_describer(self):
        pdesc = PeriodDescriber(Datetime(2021, 1, 1, 12))
        assert isinstance(pdesc, PeriodDescriber)
        p1 = Period(Datetime(2021, 1, 1, 18), Datetime(2021, 1, 2, 7))
        p2 = Period(Datetime(2021, 1, 2, 8), Datetime(2021, 1, 2, 16))
        p3 = Period(Datetime(2021, 1, 2, 17), Datetime(2021, 1, 3, 8))
        assert pdesc.describe(p1) == "de ce vendredi soir au petit matin samedi"
        assert pdesc.describe([p1, p2]) == "de ce vendredi soir à samedi après-midi"
        assert pdesc.describe([p1, p3]) == (
            "de ce vendredi soir au petit matin samedi et de samedi après-midi "
            "jusqu'au petit matin dimanche"
        )
        assert pdesc.reduce(Periods()) == []
        assert pdesc.reduce(Periods([p1, p2, p3])) == Periods(
            [Period(p1.begin_time, p3.end_time)]
        )

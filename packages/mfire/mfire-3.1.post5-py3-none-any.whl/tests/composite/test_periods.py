import pytest

from mfire.composite import PeriodCollection
from mfire.utils.date import Datetime
from tests.composite.factories import PeriodFactory


class TestPeriod:
    def test_init_boundaries(self):
        period = PeriodFactory(start="2023-03-01", stop="2023-03-03")
        assert period.start == Datetime(2023, 3, 1)
        assert period.stop == Datetime(2023, 3, 3)


class TestPeriodCollection:
    def test_attributes(self):
        p1 = PeriodFactory(id="id1")
        p2 = PeriodFactory(id="id2")
        period_collection = PeriodCollection(periods=[p1, p2])

        assert len(period_collection) == 2

        assert period_collection["id1"] == p1
        assert list(iter(period_collection)) == [p1, p2]

        with pytest.raises(KeyError, match="id3"):
            _ = period_collection["id3"]

        assert period_collection.get("id2") == p2
        assert period_collection.get("id3") is None

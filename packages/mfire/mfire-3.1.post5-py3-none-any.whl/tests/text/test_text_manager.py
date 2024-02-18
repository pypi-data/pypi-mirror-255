import pytest

from mfire.text.text_manager import TextManager
from mfire.utils.date import Datetime
from tests.composite.factories import PeriodFactory, TextComponentCompositeFactory


class TestTextManager:
    @pytest.mark.parametrize(
        "period_start,production_datetime",
        [
            (Datetime("20230301T07"), Datetime("20230102")),
            (Datetime("20230102"), Datetime("20230301T06")),
        ],
    )
    def test_compute_empty(self, period_start, production_datetime):
        period = PeriodFactory(start=period_start, stop=Datetime("20230302T06"))
        component = TextComponentCompositeFactory(
            period=period, production_datetime=production_datetime
        )
        manager = TextManager(component=component)

        assert manager.compute() == "De mercredi 01 à 08h jusqu'au jeudi 02 à 07h :\n"

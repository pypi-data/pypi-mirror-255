from typing import Iterable

import pytest
from pydantic import ValidationError

import mfire.composite as composite
from mfire.configuration.periods import (
    PeriodCollectionConfig,
    PeriodElementConfig,
    PeriodMultipleElementConfig,
    PeriodSingleElementConfig,
)
from mfire.utils.date import Datetime


class TestPeriodElementConfig:

    starts = [
        {"Start": 6},
        {"start": 6},
        {"deltaStart": 1},
        {"absoluStart": "20210101T000000"},
    ]
    stops = [
        {"stop": 12},
        {"deltaStop": 24},
        {"absoluStop": "2021-01-02T00:00:00"},
        {"Stop": 12},
    ]

    @pytest.mark.parametrize("start", starts)
    @pytest.mark.parametrize("stop", stops)
    def test_init(self, start, stop):
        assert PeriodElementConfig(**start, **stop)
        dico = {"productionTime_until": 9}
        dico.update(**start, **stop)
        assert PeriodElementConfig(**dico)

    def test_init_fail(self):
        dico = {"productionTime_until": 9}
        with pytest.raises(ValidationError):
            PeriodElementConfig(**dico)

        dico.update(**self.starts[0], **self.stops[0])
        with pytest.raises(ValidationError):
            PeriodElementConfig(**dico, **self.starts[1])
        with pytest.raises(ValidationError):
            PeriodElementConfig(**dico, **self.stops[1])

    def test_get_bound_datetime(self):
        element = PeriodElementConfig(deltaStart=1, stop=20, productionTime_until=16)
        prod_df = Datetime(2021, 1, 1, 16)
        assert element.get_bound_datetime(prod_df, "start") == Datetime(2021, 1, 1, 17)
        assert element.get_bound_datetime(prod_df, "stop") == Datetime(2021, 1, 1, 20)
        prod_df = Datetime(2021, 1, 1, 17)
        assert element.get_bound_datetime(prod_df, "start") == Datetime(2021, 1, 1, 18)
        assert element.get_bound_datetime(prod_df, "stop") == Datetime(2021, 1, 2, 20)

        element = PeriodElementConfig(
            start=6, absoluStop=Datetime(2021, 1, 3, 12), productionTime_until=16
        )
        assert element.get_bound_datetime(prod_df, "start") == Datetime(2021, 1, 2, 6)
        assert element.get_bound_datetime(prod_df, "stop") == Datetime(2021, 1, 3, 12)


class TestPeriodSingleElementConfig:
    base = {"id": "my_id", "name": "my_name"}
    dico = {"deltaStart": 1, "stop": 32, "productionTime_until": 16}

    def test_get_processed_period(self):
        period = PeriodSingleElementConfig(**self.base, **self.dico)
        prod_df1 = Datetime(2021, 1, 1, 16)
        processed_period1 = composite.Period(
            **self.base,
            start=Datetime(2021, 1, 1, 17),
            stop=Datetime(2021, 1, 2, 8),
        )
        assert period.get_processed_period(prod_df1) == processed_period1

        prod_df2 = Datetime(2021, 1, 1, 17)
        processed_period2 = composite.Period(
            **self.base,
            start=Datetime(2021, 1, 1, 18),
            stop=Datetime(2021, 1, 3, 8),
        )
        assert period.get_processed_period(prod_df2) == processed_period2


class TestPeriodMultipleElementConfig:
    base = {"id": "my_id", "name": "my_name"}
    dico = {
        "periodElements": [
            {
                "start": 6,
                "stop": 18,
                "productionTime_until": 6,
            },
            {
                "deltaStart": 1,
                "deltaStop": 12,
                "productionTime_until": 12,
            },
            {
                "absoluStart": "2021-01-01T18:00:00",
                "absoluStop": "20210102T060000",
                "productionTime_until": 18,
            },
        ]
    }

    def test_get_processed_period(self):
        period = PeriodMultipleElementConfig(**self.base, **self.dico)

        prod_df1 = Datetime(2021, 1, 1, 6)
        processed_period1 = composite.Period(
            **self.base,
            start=Datetime(2021, 1, 1, 6),
            stop=Datetime(2021, 1, 1, 18),
        )
        assert period.get_processed_period(prod_df1) == processed_period1

        prod_df2 = Datetime(2021, 1, 1, 7)
        processed_period2 = composite.Period(
            **self.base,
            start=Datetime(2021, 1, 1, 8),
            stop=Datetime(2021, 1, 1, 19),
        )
        assert period.get_processed_period(prod_df2) == processed_period2

        prod_df3 = Datetime(2021, 1, 1, 12)
        processed_period3 = composite.Period(
            **self.base,
            start=Datetime(2021, 1, 1, 13),
            stop=Datetime(2021, 1, 2, 0),
        )
        assert period.get_processed_period(prod_df3) == processed_period3

        prod_df4 = Datetime(2021, 1, 1, 13)
        processed_period4 = composite.Period(
            **self.base,
            start=Datetime(2021, 1, 1, 18),
            stop=Datetime(2021, 1, 2, 6),
        )
        assert period.get_processed_period(prod_df4) == processed_period4

        prod_df5 = Datetime(2021, 1, 1, 18)
        assert period.get_processed_period(prod_df5) == processed_period4

        prod_df6 = Datetime(2021, 1, 1, 19)
        processed_period6 = composite.Period(
            **self.base, start=Datetime(2021, 1, 2, 6), stop=Datetime(2021, 1, 2, 18)
        )
        assert period.get_processed_period(prod_df6) == processed_period6


class TestPeriodCollectionConfig:

    dico_single = {"deltaStart": 1, "stop": 32, "productionTime_until": 16}
    dico_multiple = {
        "periodElements": [
            {
                "start": 6,
                "stop": 18,
                "productionTime_until": 6,
            },
            {
                "deltaStart": 1,
                "deltaStop": 12,
                "productionTime_until": 12,
            },
            {
                "absoluStart": "2021-01-01T18:00:00",
                "absoluStop": "20210102T060000",
                "productionTime_until": 18,
            },
        ]
    }

    def test_get_processed_periods(self):
        dico_single_full = dict(id="dico1", **self.dico_single)
        dico_multiple_full = dict(id="dico2", **self.dico_multiple)
        perco = PeriodCollectionConfig(periods=[dico_single_full, dico_multiple_full])
        assert isinstance(perco.periods[0], PeriodSingleElementConfig)
        assert isinstance(perco.periods[1], PeriodMultipleElementConfig)
        assert len(perco) == len(perco.periods) == 2
        assert isinstance(list(iter(perco)), Iterable)

        assert perco["dico1"] == perco.get("dico1") == perco.periods[0]
        assert perco["dico2"] == perco.get("dico2") == perco.periods[1]
        assert perco.get("toto") is None
        assert perco.get("toto", "tata") == "tata"

        with pytest.raises(KeyError):
            _ = perco["toto"]

        processed_periods = perco.get_processed_periods(Datetime(2021, 1, 1, 6))
        assert isinstance(processed_periods, composite.PeriodCollection)

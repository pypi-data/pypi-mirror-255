from collections import defaultdict
from datetime import datetime, timedelta
from itertools import product
from pathlib import Path
from random import sample
from typing import Optional
from unittest.mock import patch

import pytest

from mfire.composite import TextComponentComposite
from mfire.text.text_manager import TextManager
from mfire.text.weather import (
    WeatherBuilder,
    WeatherDirector,
    WeatherReducer,
    WeatherSelector,
)
from mfire.utils import JsonFile, recursive_format
from mfire.utils.date import Timedelta
from tests.composite.factories import WeatherCompositeFactory
from tests.utils.test_wwmf_utils import dataset_wwmf_label


class TestWeatherSelector:
    def test_0_ts(self):
        selector = WeatherSelector()
        reduction = {}
        assert selector.compute(reduction) == "0xTS"

    @pytest.mark.parametrize(
        "temp,severe,expected",
        [
            (None, False, "1xTS"),
            ("temp", False, "1xTS_temp"),
            (None, True, "1xTS_severe"),
            ("temp", True, "1xTS_temp_severe"),
        ],
    )
    def test_1_ts(self, temp, severe, expected):
        selector = WeatherSelector()
        reduction = {
            "TS1": {
                "temporality": temp,
                "localisation": ...,
                "label": ...,
            }
        }
        if severe:
            reduction["TSsevere"] = ...
        assert selector.compute(reduction) == expected

    @pytest.mark.parametrize(
        "temp1,temp2,severe,expected",
        [
            # without severe sentence
            (None, None, False, "2xTS"),
            ("temp", None, False, "2xTS_temp1"),
            (None, "temp", False, "2xTS_temp2"),
            ("temp", "temp", False, "2xTS_temp"),
            # with severe sentence
            (None, None, True, "2xTS_severe"),
            ("temp", None, True, "2xTS_temp1_severe"),
            (None, "temp", True, "2xTS_temp2_severe"),
            ("temp", "temp", True, "2xTS_temp_severe"),
        ],
    )
    def test_2_ts(self, temp1, temp2, severe, expected):
        selector = WeatherSelector()
        reduction = {
            "TS1": {
                "temporality": temp1,
                "localisation": ...,
                "label": ...,
            },
            "TS2": {
                "temporality": temp2,
                "localisation": ...,
                "label": ...,
            },
        }
        if severe:
            reduction["TSsevere"] = ...
        assert selector.compute(reduction) == expected

    @pytest.mark.parametrize(
        "temp1,temp2,temp3,expected",
        [
            (None, None, None, "3xTS"),
            ("temp", None, None, "3xTS_temp1"),
            (None, "temp", None, "3xTS_temp2"),
            (None, None, "temp", "3xTS_temp3"),
            ("temp", "temp", None, "3xTS_temp12"),
            ("temp", None, "temp", "3xTS_temp13"),
            (None, "temp", "temp", "3xTS_temp23"),
            ("temp", "temp", "temp", "3xTS_temp123"),
        ],
    )
    def test_3_ts(self, temp1, temp2, temp3, expected):
        selector = WeatherSelector()
        reduction = {
            "TS1": {
                "temporality": temp1,
                "localisation": ...,
                "label": ...,
            },
            "TS2": {
                "temporality": temp2,
                "localisation": ...,
                "label": ...,
            },
            "TS3": {
                "temporality": temp3,
                "localisation": ...,
                "label": ...,
            },
        }
        assert selector.compute(reduction) == expected

    def test_unimplemented(self):
        selector = WeatherSelector()
        reduction = {
            "TS1": ...,
            "TS2": ...,
            "TS3": ...,
            "TS4": ...,
        }
        assert selector.compute(reduction) == "Unimplemented"


class TestWeatherBuilder:
    def test_0_ts(self):
        builder = WeatherBuilder()
        reduction = {}

        builder.compute(reduction)
        assert builder.text == ("Temps sec.")

    @pytest.mark.parametrize("temp,loc,severe", product([True, False], repeat=3))
    def test_1_ts(self, temp, loc, severe, assert_equals_result):
        builder = WeatherBuilder()
        reduction = {
            "TS1": {
                "label": "neige",
                "temporality": "le mercredi matin" if temp else "",
                "localisation": "au-dessus de 500m" if loc else "",
            }
        }
        if severe:
            reduction["TSsevere"] = {
                "label": "orages violents",
                "localisation": "au Nord",
            }
        builder.compute(reduction)
        assert_equals_result(builder.text)

    @pytest.mark.parametrize(
        "temp1,loc1,temp2,loc2,severe", product([True, False], repeat=5)
    )
    def test_2_ts(self, temp1, loc1, temp2, loc2, severe, assert_equals_result):
        builder = WeatherBuilder()

        reduction = {
            "TS1": {
                "label": "neige faible",
                "temporality": "le mercredi matin" if temp1 else None,
                "localisation": "au-dessus de 500m" if loc1 else "",
            },
            "TS2": {
                "label": "neige modérée",
                "temporality": "le jeudi matin" if temp2 else None,
                "localisation": "au-dessus de 800m" if loc2 else "",
            },
        }
        if severe:
            reduction["TSsevere"] = {
                "label": "orages violents",
                "localisation": "au Nord",
            }
        builder.compute(reduction)
        assert_equals_result(builder.text)

    @pytest.mark.parametrize(
        "temp1,loc1,temp2,loc2,temp3,loc3", product([True, False], repeat=6)
    )
    def test_3_ts(self, temp1, loc1, temp2, loc2, temp3, loc3, assert_equals_result):
        builder = WeatherBuilder()
        reduction = {
            "TS1": {
                "temporality": "Mardi matin" if temp1 else None,
                "localisation": "au-dessus de 1000 m" if loc1 else "",
                "label": "neige faible",
            },
            "TS2": {
                "temporality": "Mercredi après-midi" if temp2 else None,
                "localisation": "au-dessus de 800 m" if loc2 else "",
                "label": "neige modérée",
            },
            "TS3": {
                "temporality": "Jeudi soir" if temp3 else None,
                "localisation": "au-dessus de 300 m" if loc3 else "",
                "label": "neige forte",
            },
        }
        builder.compute(reduction)
        assert_equals_result(builder.text)


class TestWeatherReducer:
    """
    This test ensures that the good isolated phenomenon are excluded,
    severe phenomenon are not excluded, indicated localisation for snow, ...
    Thresholds are bigger in order to see the exclusions
    """

    def _compute(
        self,
        codes: list,
        valid_times: list,
        units: str = "wwmf",
        lon: Optional[list] = None,
        lat: Optional[list] = None,
        altitude: Optional[list] = None,
        geos_descriptive: Optional[list] = None,
        requiredDT: float = 0.05,
        requiredDHmax: float = 0.05,
    ):
        if lat is None:
            lat = [30, 31]
        if lon is None:
            lon = [40, 41]
        if geos_descriptive is None:
            geos_descriptive = [[[1] * len(lon)] * len(lat)]
        if altitude is None:
            altitude = [[0] * len(lon)] * len(lat)

        data_vars = {
            "wwmf": (
                ["valid_time", "latitude", "longitude"],
                codes,
                {"units": units},
            )
        }

        composite = WeatherCompositeFactory.create_factory(
            geos_descriptive=geos_descriptive,
            valid_times=valid_times,
            lon=lon,
            lat=lat,
            data_vars=data_vars,
            altitude=altitude,
        )

        self.reducer = WeatherReducer()
        self.reducer.required_DT = defaultdict(lambda: requiredDT)
        self.reducer.required_DHmax = defaultdict(lambda: requiredDHmax)
        return self.reducer.compute(geo_id="id_axis", composite=composite)

    def test_1_valid_time(self):
        valid_times = [
            datetime(2023, 3, 1),
        ]
        lon, lat = [40], [35]
        assert (
            self._compute(codes=[[[0]]], lon=lon, lat=lat, valid_times=valid_times)
            == {}
        )

    @pytest.mark.parametrize(
        "codes",
        [
            # No possible loc since all IoL < 0.2 => altitudes are taken
            ([[0, 0, 0], [60, 0, 0], [0, 0, 0]]),
            # When IoL < 0.2 and the difference between the lowest point of TS and
            # map < 100m #38200
            ([[0, 0, 0], [0, 0, 0], [0, 60, 0]]),
            # When IoL < 0.2 and the lowest point is between 0 and 100 m
            ([[0, 0, 0], [0, 60, 0], [0, 0, 0]]),
            # When IoL < 0.2 and no snow
            ([[0, 0, 0], [50, 0, 0], [0, 0, 0]]),
            # Loc 2 isn't taken since IoL = 1/6 < 0.2
            ([[60, 0, 0], [0, 0, 0], [0, 0, 0]]),
            # Loc 2 is taken since IoL > 0.2
            ([[60, 60, 0], [0, 0, 0], [0, 0, 0]]),
            # Several loc
            ([[60, 0, 60], [0, 0, 60], [0, 0, 60]]),
            # all domain is taken
            ([[60, 60, 60], [60, 60, 60], [60, 60, 60]]),
            # Only loc 3
            ([[60, 60, 0], [60, 60, 0], [60, 60, 0]]),
            # Loc 3 and 1 are taken but these zones cover all domain
            ([[60, 60, 60], [60, 60, 0], [60, 60, 0]]),
        ],
    )
    def test_localisation_rules(self, codes, assert_equals_result):
        lon = [40, 41, 42]
        lat = [35, 36, 37]
        valid_times = [datetime(2023, 3, 1), datetime(2023, 3, 2)]

        geos_descriptive = [
            [[0, 0, 1], [0, 0, 1], [0, 0, 1]],
            [[1, 1, 0], [0, 0, 0], [0, 0, 0]],
            [[1, 1, 0], [1, 1, 0], [1, 1, 0]],
        ]
        altitude = [[100, 125, 345], [241, 10, 368], [-200, -150, 389]]

        assert_equals_result(
            self._compute(
                codes=2 * [codes],
                lon=lon,
                lat=lat,
                valid_times=valid_times,
                geos_descriptive=geos_descriptive,
                altitude=altitude,
                requiredDT=0,  # in order to not exclude isolated point
                requiredDHmax=0,  # in order to not exclude isolated point
            )
        )

    @pytest.mark.parametrize(
        "codes",
        [
            # Indicated phenomenon must last at least 3h
            [
                [[33], [33]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
            ],
            [
                [[33], [33]],
                [[33], [33]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
            ],
            [
                [[33], [33]],
                [[33], [33]],
                [[33], [33]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
            ],
            # No discontinuity if interruption less than 3 hours
            [
                [[33], [33]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[33], [33]],
                [[33], [33]],
            ],
            [
                [[33], [33]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[33], [33]],
                [[33], [33]],
                [[33], [33]],
            ],
            [
                [[33], [33]],
                [[33], [33]],
                [[0], [0]],
                [[0], [0]],
                [[33], [33]],
                [[33], [33]],
                [[33], [33]],
            ],
            [
                [[33], [33]],
                [[33], [33]],
                [[33], [33]],
                [[0], [0]],
                [[33], [33]],
                [[33], [33]],
                [[33], [33]],
            ],
            [
                [[33], [33]],
                [[0], [0]],
                [[33], [33]],
                [[0], [0]],
                [[33], [33]],
                [[0], [0]],
                [[33], [33]],
            ],
            [
                [[33], [33]],
                [[0], [0]],
                [[33], [33]],
                [[0], [0]],
                [[0], [0]],
                [[33], [33]],
                [[33], [33]],
            ],
        ],
    )
    def test_temporality_rules(self, codes, assert_equals_result):
        """This test handles the following temporality rules:
        * if the duration is  less than 3h it is not be considered
        * if ts lasts all the time the temporality isn't indicated
        """
        valid_times = [
            datetime(2023, 3, 1, 10),
            datetime(2023, 3, 1, 11),
            datetime(2023, 3, 1, 12),
            datetime(2023, 3, 1, 13),
            datetime(2023, 3, 1, 14),
            datetime(2023, 3, 1, 15),
            datetime(2023, 3, 1, 16),
        ]
        lon, lat = [40], [35, 36]
        assert_equals_result(
            self._compute(codes=codes, lon=lon, lat=lat, valid_times=valid_times)
        )

    @pytest.mark.parametrize(
        "codes,expected_label",
        sample(dataset_wwmf_label, 10),
    )
    def test_grouping_rules(self, codes, expected_label):
        """This test handles more than 3 distinct phenomenon to ensure that they
        will be well put together"""
        valid_times = [datetime(2023, 3, 1), datetime(2023, 3, 2)]

        lon, lat = list(range(len(codes))), [35]
        codes = [
            [codes],
            [codes],
        ]

        result = self._compute(codes=codes, lon=lon, lat=lat, valid_times=valid_times)
        assert len(result) == 1
        assert result["TS1"]["label"] == expected_label

    @pytest.mark.parametrize(
        "codes",
        [
            # 1 severe TS
            [[[49, 0], [0, 0]], [[0, 0], [0, 0]]],
            [[[59, 59], [0, 0]], [[0, 0], [0, 0]]],
            [[[0, 0], [0, 85]], [[0, 0], [0, 0]]],
            [[[0, 98], [0, 0]], [[0, 0], [0, 0]]],
            [[[0, 0], [0, 0]], [[99, 0], [0, 99]]],
            # 2TS: 1 severe + 1 not severe
            [[[49, 0], [0, 0]], [[70, 0], [0, 0]]],
            [[[85, 91], [0, 0]], [[0, 0], [0, 0]]],
            # 3TS: 1 severe + 2 not severe
            [[[49, 59], [70, 0]], [[0, 0], [0, 0]]],
            [[[49, 59], [0, 0]], [[70, 0], [0, 0]]],
            [[[49, 0], [70, 0]], [[59, 0], [0, 0]]],
            [[[49, 61], [70, 0]], [[0, 0], [0, 0]]],
        ],
    )
    def test_severe_phenomenon(self, codes, assert_equals_result):
        valid_times = [datetime(2023, 3, 1), datetime(2023, 3, 2), datetime(2023, 3, 3)]

        # to avoid that the phenomenon is over all the period
        codes.append([[0, 0], [0, 0]])

        # We change the requiredDT and requiredDHmax to be able to see the exclusion
        assert_equals_result(
            self._compute(
                codes=codes,
                valid_times=valid_times,
                requiredDT=0.3,
                requiredDHmax=0.5,
            )
        )

    @pytest.mark.parametrize(
        "units,codes",
        [
            # No TS
            ("w1", [[[0, -1], [0, 0]], [[0, -1], [0, 0]]]),
            ("wwmf", [[[1, 15], [20, 25]], [[27, 29], [7, 0]]]),
            # DT<50% and DHmax<50% => excluded since isolated
            ("wwmf", [[[90, 0], [0, 0]], [[0, 90], [0, 0]]]),
            ("w1", [[[0, 0], [0, 18]], [[0, 0], [18, 0]]]),
            ("wwmf", [[[90, 0], [0, 0]], [[90, 31], [0, 0]]]),
            ("w1", [[[0, 0], [0, 17]], [[0, 17], [2, 0]]]),
        ],
    )
    def test_ras(self, units, codes):
        valid_times = [datetime(2023, 3, 1), datetime(2023, 3, 2)]

        # We change the requiredDT and requiredDHmax to be able to see the exclusion
        assert (
            self._compute(
                codes=codes,
                units=units,
                valid_times=valid_times,
                requiredDT=0.5,
                requiredDHmax=0.5,
            )
            == {}
        )

    @pytest.mark.parametrize(
        "units,codes",
        [
            # DT>30% + DHmax>50% => not isolated
            (
                "wwmf",
                [[[50, 50], [50, 50]], [[50, 50], [50, 50]]],
            ),
            (
                "w1",
                [[[9, 9], [9, 9]], [[9, 9], [9, 9]]],
            ),
            (
                "wwmf",
                [[[50, 50], [50, 50]], [[0, 0], [0, 0]]],
            ),
            (
                "w1",
                [[[0, 0], [0, 0]], [[9, 9], [9, 9]]],
            ),
            # DT<30% + DHmax>50% => not isolated
            (
                "wwmf",
                [[[33, 33], [0, 0]], [[0, 0], [0, 0]]],
            ),
            (
                "w1",
                [[[0, 0], [0, 0]], [[0, 5], [5, 0]]],
            ),
            (
                "wwmf",
                [[[33, 33], [62, 62]], [[0, 0], [0, 0]]],
            ),
            (
                "w1",
                [[[20, 0], [0, 20]], [[0, 5], [5, 0]]],
            ),
            (
                "wwmf",
                [[[33, 33], [62, 62]], [[33, 0], [62, 0]]],
            ),
            (
                "w1",
                [[[20, 5], [0, 20]], [[0, 5], [5, 20]]],
            ),
            (
                "wwmf",
                [[[31, 32], [60, 62]], [[33, 0], [61, 0]]],
            ),
            (
                "w1",
                [[[19, 4], [0, 20]], [[0, 5], [6, 21]]],
            ),
            # Test the localisation (with snow code)
            (
                "wwmf",
                [[[0, 0], [58, 58]], [[0, 0], [58, 58]]],
            ),
            (
                "w1",
                [[[13, 13], [13, 13]], [[0, 0], [0, 0]]],
            ),
            # Test of code with nebulosity replacement
            (
                "wwmf",
                [[[72, 72], [72, 72]], [[0, 0], [0, 0]]],
            ),
            (
                "wwmf",
                [[[73, 73], [73, 73]], [[0, 0], [0, 0]]],
            ),
            (
                "wwmf",
                [[[0, 78], [0, 78]], [[0, 0], [78, 78]]],
            ),
            (
                "wwmf",
                [[[82, 82], [82, 0]], [[0, 82], [0, 0]]],
            ),
            (
                "wwmf",
                [[[83, 83], [83, 83]], [[0, 0], [0, 0]]],
            ),
            # 2TS but one with DT<30%
            (
                "wwmf",
                [[[50, 50], [50, 50]], [[31, 50], [31, 50]]],
            ),
            # 2TS but one with DT<30% and DHmax<50%
            (
                "wwmf",
                [[[50, 50], [50, 50]], [[31, 50], [0, 50]]],
            ),
        ],
    )
    def test_1_ts(self, units, codes, assert_equals_result):
        valid_times = [datetime(2023, 3, 1), datetime(2023, 3, 2), datetime(2023, 3, 3)]
        altitude = [[1045, 1501], [2040, 2509]]

        # to avoid that the phenomenon is over all the period
        codes.append([[0, 0], [0, 0]])

        # We change the requiredDT and requiredDHmax to be able to see the exclusion
        assert_equals_result(
            self._compute(
                codes=codes,
                units=units,
                valid_times=valid_times,
                altitude=altitude,
                requiredDT=0.3,
                requiredDHmax=0.5,
            )
        )

    @pytest.mark.parametrize(
        "units,codes",
        [
            # 2TS with different families
            (
                "wwmf",
                (50, 31),
            ),
            (
                "w1",
                (3, 9),
            ),
            # Localisation with snow
            (
                "wwmf",
                (31, 60),
            ),
            (
                "w1",
                (13, 2),
            ),
            (
                "wwmf",
                (62, 63),
            ),
            (
                "w1",
                (16, 17),
            ),
        ],
    )
    def test_2_ts_different_families(self, units, codes, assert_equals_result):
        """
        This test handles simple cases with 2 TS over 2 valid_times
        """
        valid_times = [datetime(2023, 3, 1), datetime(2023, 3, 2), datetime(2023, 3, 3)]
        altitude = [[1070], [2099]]

        lon, lat = [40], [35, 36]
        codes = [
            [[codes[0]], [codes[0]]],
            [[codes[1]], [codes[1]]],
            [[0], [0]],  # to avoid that the phenomenon is over all the period
        ]
        assert_equals_result(
            self._compute(
                codes=codes,
                lon=lon,
                lat=lat,
                units=units,
                valid_times=valid_times,
                altitude=altitude,
            )
        )

    @pytest.mark.parametrize(
        "units,codes,durations",
        [
            # 2 TS not severe with 2 (<3) hours of covering and
            # 0.2 (<0.25) proportion of coverage => 2 distinct TS
            (
                "wwmf",
                (70, 61),
                (10, 2, 10),
            ),
            (
                "w1",
                (2, 6),
                (10, 2, 10),
            ),
            # 2 TS not severe with 4 (>3) hours of covering and
            # 0.2 (<0.25) proportion of coverage => 2 distinct TS
            (
                "wwmf",
                (70, 61),
                (20, 4, 20),
            ),
            (
                "w1",
                (2, 6),
                (20, 4, 20),
            ),
            # 2 TS not severe with 2 (<3) hours of covering and
            # 0.5 (>0.25) proportion of coverage => 2 distinct TS
            (
                "wwmf",
                (70, 61),
                (4, 2, 4),
            ),
            (
                "w1",
                (2, 6),
                (4, 2, 4),
            ),
            # 2 TS not severe with 4 (>3) hours of covering and
            # 0.4 (>0.25) proportion of coverage => same TS
            (
                "wwmf",
                (70, 61),
                (10, 4, 10),
            ),
            (
                "w1",
                (2, 6),
                (10, 4, 10),
            ),
            # 2 precipitation TS which 1 severe with 0.4 (>0.25) proportion of
            # intersection  => 2 distinct TS
            # Notice that if it was not severe it would consider as same TS
            (
                "wwmf",
                (70, 98),
                (10, 4, 10),
            ),
            # 2 precipitation TS which 1 severe with 0.78 (>0.75) proportion of
            # intersection  => same TS
            (
                "wwmf",
                (70, 98),
                (1, 7, 1),
            ),
        ],
    )
    def test_2_ts_same_families(self, units, codes, durations, assert_equals_result):
        """
        This test handles 2 TS  with valid_times which duration is given.
        The first and second period lasts duration[0] and the third one duration[1]
        """
        d0 = datetime(2023, 3, 1)
        valid_times = [
            d0,
            d0 + timedelta(hours=durations[0]),
            d0 + timedelta(hours=durations[0] + durations[1]),
            d0 + timedelta(hours=durations[0] + durations[1] + durations[2]),
        ]

        lon, lat = [40], [35, 36]
        codes = [
            [[0], [0]],
            [[codes[0]], [codes[0]]],
            [[codes[0]], [codes[1]]],
            [[codes[1]], [codes[1]]],
        ]
        assert_equals_result(
            self._compute(
                codes=codes, lon=lon, lat=lat, units=units, valid_times=valid_times
            )
        )

    @pytest.mark.parametrize(
        "codes,durations",
        [
            # 3 visibility TS
            (
                (30, 32, 33),
                (1, 4),
            ),
            (
                (30, 32, 33),
                (4, 1),
            ),
            # 3 precipitation TS with 2 subfamily
            (
                (51, 52, 60),
                (1, 4),
            ),
            (
                (51, 58, 70),
                (4, 1),
            ),
            # 3 precipitation TS with 1 subfamily
            (
                (51, 52, 53),
                (1, 4),
            ),
            (
                (61, 62, 63),
                (4, 1),
            ),
            (
                (70, 71, 77),
                (1, 4),
            ),
            # 3 precipitation TS with 2 precipitations + 1 visibility
            (
                (32, 71, 77),
                (1, 4),
            ),
            (
                (32, 70, 61),
                (4, 1),
            ),
            (
                (71, 32, 77),
                (1, 4),
            ),
            # 3 precipitation TS with 2 visibilities + 1 precipitation
            (
                (32, 33, 77),
                (4, 1),
            ),
            (
                (32, 30, 61),
                (1, 4),
            ),
            (
                (32, 77, 33),
                (4, 1),
            ),
            # Phenomenon which can't be grouped by pair (according to their temporality)
            (
                (51, 71, 52),
                (2, 2),
            ),
        ],
    )
    def test_3_ts_temporalities(self, codes, durations, assert_equals_result):
        """This test handles 3 phenomenon with two of same temporality
        to ensure that they will be well put together"""
        valid_times = [
            datetime(2023, 3, 1, 0),
            datetime(2023, 3, 1, 3),
            datetime(2023, 3, 1, 3 + durations[0]),
            datetime(2023, 3, 1, 3 + durations[0] + durations[1]),
            datetime(2023, 3, 1, 3 + durations[0] + durations[1] + 3),
        ]

        lon, lat = [40], [35, 36]
        codes = [
            [[0], [0]],
            [[codes[0]], [codes[0]]],
            [[codes[0]], [codes[1]]],
            [[codes[1]], [codes[2]]],
            [[codes[2]], [codes[2]]],
        ]
        assert_equals_result(
            self._compute(codes=codes, lon=lon, lat=lat, valid_times=valid_times)
        )

    @pytest.mark.parametrize(
        "codes",
        [
            # >3 visibility TS
            ([[[31, 32], [33, 38]], [[0, 0], [0, 0]]]),
            ([[[31, 32], [33, 38]], [[31, 39], [0, 0]]]),
            # 3 visibility TS and 1 precipitation
            ([[[31, 32], [33, 60]], [[0, 0], [0, 0]]]),
            # 2 visibility TS and 2 precipitation
            ([[[31, 61], [33, 60]], [[0, 0], [0, 0]]]),
            # 1 visibility TS and 3 precipitation
            ([[[31, 62], [63, 60]], [[0, 0], [0, 0]]]),
            # >3 precipitation TS and no severe
            ([[[51, 61], [70, 71]], [[0, 0], [0, 0]]]),
            ([[[51, 61], [70, 71]], [[80, 0], [0, 0]]]),
            ([[[51, 61], [70, 71]], [[80, 91], [0, 0]]]),
            ([[[51, 61], [70, 71]], [[80, 90], [70, 0]]]),
            ([[[51, 61], [70, 71]], [[80, 90], [50, 60]]]),
            # >3 precipitation TS and 1 severe
            ([[[51, 61], [70, 71]], [[98, 0], [0, 0]]]),
            ([[[51, 61], [70, 71]], [[98, 99], [0, 0]]]),
            ([[[51, 61], [70, 84]], [[98, 71], [0, 85]]]),
            # several precipitation + visibility TS
            ([[[51, 32], [0, 0]], [[0, 0], [84, 92]]]),
            ([[[51, 32], [33, 71]], [[80, 0], [0, 0]]]),
            ([[[51, 32], [33, 71]], [[33, 91], [83, 92]]]),
            ([[[51, 32], [33, 71]], [[33, 91], [83, 38]]]),
            ([[[51, 32], [33, 71]], [[33, 91], [83, 98]]]),
            # If there is only 2 visibilities with 31 (Haze)
            # => the code and temporality of haze aren't included
            ([[[31, 32], [60, 61]], [[31, 0], [0, 0]]]),
            # If there is at least 3 visibilities with 31 (Haze)
            # => the temporality of haze isn't included
            ([[[31, 32], [33, 61]], [[31, 60], [0, 0]]]),
            ([[[31, 32], [33, 38]], [[31, 60], [61, 0]]]),
        ],
    )
    def test_more_than_3_ts_temporalities(self, codes, assert_equals_result):
        valid_times = [
            datetime(2023, 3, 1),
            datetime(2023, 3, 2),
            datetime(2023, 3, 3),
        ]

        # to avoid that the phenomenon is over all the period
        codes.append(
            [
                [0, 0],
                [0, 0],
            ]
        )
        assert_equals_result(self._compute(codes=codes, valid_times=valid_times))


class TestWeatherDirector:
    @staticmethod
    def _compute(
        codes: list,
        valid_times: list,
        units: str = "wwmf",
        lon: Optional[list] = None,
        lat: Optional[list] = None,
        altitude: Optional[list] = None,
        geos_descriptive: Optional[list] = None,
        requiredDT: float = 0.05,
        requiredDHmax: float = 0.05,
    ):
        if lat is None:
            lat = [30, 31]
        if lon is None:
            lon = [40, 41]
        if geos_descriptive is None:
            geos_descriptive = [[[1] * len(lon)] * len(lat)]
        if altitude is None:
            altitude = [[0] * len(lon)] * len(lat)

        data_vars = {
            "wwmf": (
                ["valid_time", "latitude", "longitude"],
                codes,
                {"units": units},
            )
        }

        composite = WeatherCompositeFactory.create_factory(
            geos_descriptive=geos_descriptive,
            valid_times=valid_times,
            lon=lon,
            lat=lat,
            data_vars=data_vars,
            altitude=altitude,
        )

        director = WeatherDirector()
        director.reducer.required_DT = defaultdict(lambda: requiredDT)
        director.reducer.required_DHmax = defaultdict(lambda: requiredDHmax)
        return director.compute(geo_id="id_axis", composite=composite)

    def test_1_valid_time(self):
        valid_times = [
            datetime(2023, 3, 1),
        ]
        lon, lat = [40], [35]
        assert (
            self._compute(codes=[[[0]]], lon=lon, lat=lat, valid_times=valid_times)
            == "Temps sec."
        )

    @pytest.mark.parametrize(
        "codes",
        [
            # No possible loc since all IoL < 0.2 => altitudes are taken
            ([[0, 0, 0], [60, 0, 0], [0, 0, 0]]),
            # When IoL < 0.2 and the difference between the lowest point of TS and
            # map < 100m #38200
            ([[0, 0, 0], [0, 0, 0], [0, 60, 0]]),
            # When IoL < 0.2 and the lowest point is between 0 and 100 m
            ([[0, 0, 0], [0, 60, 0], [0, 0, 0]]),
            # When IoL < 0.2 and no snow
            ([[0, 0, 0], [50, 0, 0], [0, 0, 0]]),
            # Loc 2 isn't taken since IoL = 1/6 < 0.2
            ([[60, 0, 0], [0, 0, 0], [0, 0, 0]]),
            # Loc 2 is taken since IoL > 0.2
            ([[60, 60, 0], [0, 0, 0], [0, 0, 0]]),
            # Several loc
            ([[60, 0, 60], [0, 0, 60], [0, 0, 60]]),
            # all domain is taken
            ([[60, 60, 60], [60, 60, 60], [60, 60, 60]]),
            # Only loc 3
            ([[60, 60, 0], [60, 60, 0], [60, 60, 0]]),
            # Loc 3 and 1 are taken but these zones cover all domain
            ([[60, 60, 60], [60, 60, 0], [60, 60, 0]]),
        ],
    )
    def test_localisation_rules(self, codes, assert_equals_result):
        lon = [40, 41, 42]
        lat = [35, 36, 37]
        valid_times = [datetime(2023, 3, 1), datetime(2023, 3, 2)]

        geos_descriptive = [
            [[0, 0, 1], [0, 0, 1], [0, 0, 1]],
            [[1, 1, 0], [0, 0, 0], [0, 0, 0]],
            [[1, 1, 0], [1, 1, 0], [1, 1, 0]],
        ]
        altitude = [[100, 125, 345], [241, 10, 368], [-200, -150, 389]]

        assert_equals_result(
            self._compute(
                codes=2 * [codes],
                lon=lon,
                lat=lat,
                valid_times=valid_times,
                geos_descriptive=geos_descriptive,
                altitude=altitude,
                requiredDT=0,  # in order to not exclude isolated point
                requiredDHmax=0,  # in order to not exclude isolated point
            )
        )

    @pytest.mark.parametrize(
        "codes",
        [
            # Indicated phenomenon must last at least 3h
            [
                [[33], [33]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
            ],
            [
                [[33], [33]],
                [[33], [33]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
            ],
            [
                [[33], [33]],
                [[33], [33]],
                [[33], [33]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
            ],
            # No discontinuity if interruption less than 3 hours
            [
                [[33], [33]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[33], [33]],
                [[33], [33]],
            ],
            [
                [[33], [33]],
                [[0], [0]],
                [[0], [0]],
                [[0], [0]],
                [[33], [33]],
                [[33], [33]],
                [[33], [33]],
            ],
            [
                [[33], [33]],
                [[33], [33]],
                [[0], [0]],
                [[0], [0]],
                [[33], [33]],
                [[33], [33]],
                [[33], [33]],
            ],
            [
                [[33], [33]],
                [[33], [33]],
                [[33], [33]],
                [[0], [0]],
                [[33], [33]],
                [[33], [33]],
                [[33], [33]],
            ],
            [
                [[33], [33]],
                [[0], [0]],
                [[33], [33]],
                [[0], [0]],
                [[33], [33]],
                [[0], [0]],
                [[33], [33]],
            ],
            [
                [[33], [33]],
                [[0], [0]],
                [[33], [33]],
                [[0], [0]],
                [[0], [0]],
                [[33], [33]],
                [[33], [33]],
            ],
        ],
    )
    def test_temporality_rules(self, codes, assert_equals_result):
        """This test handles the temporality rule: if the duration is
        less than 3h it is not be considered"""
        valid_times = [
            datetime(2023, 3, 1, 10),
            datetime(2023, 3, 1, 11),
            datetime(2023, 3, 1, 12),
            datetime(2023, 3, 1, 13),
            datetime(2023, 3, 1, 14),
            datetime(2023, 3, 1, 15),
            datetime(2023, 3, 1, 16),
        ]
        lon, lat = [40], [35, 36]
        assert_equals_result(
            self._compute(codes=codes, lon=lon, lat=lat, valid_times=valid_times)
        )

    @pytest.mark.parametrize(
        "codes,expected_label",
        sample(dataset_wwmf_label, 10),
    )
    def test_grouping_rules(self, codes, expected_label):
        """This test handles more than 3 distinct phenomenon to ensure that they
        will be well put together"""
        valid_times = [datetime(2023, 3, 1), datetime(2023, 3, 2)]

        lon, lat = list(range(len(codes))), [35]
        codes = [
            [codes],
            [codes],
        ]

        assert self._compute(
            codes=codes, lon=lon, lat=lat, valid_times=valid_times
        ).startswith(expected_label)

    @pytest.mark.parametrize(
        "codes",
        [
            # 1 severe TS
            [[[49, 0], [0, 0]], [[0, 0], [0, 0]]],
            [[[59, 59], [0, 0]], [[0, 0], [0, 0]]],
            [[[0, 0], [0, 85]], [[0, 0], [0, 0]]],
            [[[0, 98], [0, 0]], [[0, 0], [0, 0]]],
            [[[0, 0], [0, 0]], [[99, 0], [0, 99]]],
            # 2TS: 1 severe + 1 not severe
            [[[49, 0], [0, 0]], [[70, 0], [0, 0]]],
            [[[85, 91], [0, 0]], [[0, 0], [0, 0]]],
            # 3TS: 1 severe + 2 not severe
            [[[49, 59], [70, 0]], [[0, 0], [0, 0]]],
            [[[49, 59], [0, 0]], [[70, 0], [0, 0]]],
            [[[49, 0], [70, 0]], [[59, 0], [0, 0]]],
            [[[49, 61], [70, 0]], [[0, 0], [0, 0]]],
        ],
    )
    def test_severe_phenomenon(self, codes, assert_equals_result):
        valid_times = [datetime(2023, 3, 1), datetime(2023, 3, 2), datetime(2023, 3, 3)]

        # to avoid that the phenomenon is over all the period
        codes.append([[0, 0], [0, 0]])

        # We change the requiredDT and requiredDHmax to be able to see the exclusion
        assert_equals_result(
            self._compute(
                codes=codes,
                valid_times=valid_times,
                requiredDT=0.3,
                requiredDHmax=0.5,
            )
        )

    @pytest.mark.parametrize(
        "units,codes",
        [
            # No TS
            ("w1", [[[0, 0], [0, 0]], [[0, -1], [0, 0]]]),
            ("wwmf", [[[1, 15], [20, 25]], [[27, 29], [7, 10]]]),
            # DT<50% and DHmax<50% => excluded since isolated
            ("wwmf", [[[90, 0], [0, 0]], [[0, 90], [0, 0]]]),
            ("w1", [[[0, 0], [0, 18]], [[0, 0], [18, 0]]]),
            ("wwmf", [[[90, 0], [0, 0]], [[90, 31], [0, 0]]]),
            ("w1", [[[0, 0], [0, 17]], [[0, 17], [2, 0]]]),
        ],
    )
    def test_ras(self, units, codes):
        valid_times = [datetime(2023, 3, 1), datetime(2023, 3, 2)]

        # We change the requiredDT and requiredDHmax to be able to see the exclusion
        assert (
            self._compute(
                codes=codes,
                units=units,
                valid_times=valid_times,
                requiredDT=0.5,
                requiredDHmax=0.5,
            )
            == "Temps sec."
        )

    @pytest.mark.parametrize(
        "units,valid_times,codes",
        [
            # DT>30% and DHmax>50% => not isolated
            (
                "wwmf",
                [datetime(2023, 3, 1, 8, 0, 0), datetime(2023, 3, 1, 11, 0, 0)],
                [[[50, 50], [50, 50]], [[50, 50], [50, 50]]],
            ),
            (
                "w1",
                [datetime(2023, 3, 1, 8, 0, 0), datetime(2023, 3, 1, 20, 0, 0)],
                [[[9, 9], [9, 9]], [[9, 9], [9, 9]]],
            ),
            (
                "wwmf",
                [datetime(2023, 3, 1, 14, 0, 0), datetime(2023, 3, 1, 20, 0, 0)],
                [[[50, 50], [50, 50]], [[0, 0], [0, 0]]],
            ),
            (
                "w1",
                [datetime(2023, 3, 1, 19, 0, 0), datetime(2023, 3, 1, 22, 0, 0)],
                [[[0, 0], [0, 0]], [[9, 9], [9, 9]]],
            ),
            # DT<30% + DHmax>50% => not isolated
            (
                "wwmf",
                [datetime(2023, 3, 1), datetime(2023, 3, 2)],
                [[[33, 33], [0, 0]], [[0, 0], [0, 0]]],
            ),
            (
                "w1",
                [datetime(2023, 3, 1), datetime(2023, 3, 2)],
                [[[0, 0], [0, 0]], [[0, 5], [5, 0]]],
            ),
            (
                "wwmf",
                [datetime(2023, 3, 1), datetime(2023, 3, 2)],
                [[[33, 33], [62, 62]], [[0, 0], [0, 0]]],
            ),
            (
                "w1",
                [datetime(2023, 3, 1), datetime(2023, 3, 2)],
                [[[20, 0], [0, 20]], [[0, 5], [5, 0]]],
            ),
            (
                "wwmf",
                [datetime(2023, 3, 1), datetime(2023, 3, 2)],
                [[[33, 33], [62, 62]], [[33, 0], [62, 0]]],
            ),
            (
                "w1",
                [datetime(2023, 3, 1), datetime(2023, 3, 2)],
                [[[20, 5], [0, 20]], [[0, 5], [5, 20]]],
            ),
            (
                "wwmf",
                [datetime(2023, 3, 1), datetime(2023, 3, 2)],
                [[[31, 32], [60, 62]], [[33, 0], [61, 0]]],
            ),
            (
                "w1",
                [datetime(2023, 3, 1), datetime(2023, 3, 2)],
                [[[19, 4], [0, 20]], [[0, 5], [6, 21]]],
            ),
            # Test the localisation (with snow code)
            (
                "wwmf",
                [datetime(2023, 3, 1, 23, 0, 0), datetime(2023, 4, 1, 4, 0, 0)],
                [[[0, 0], [58, 58]], [[0, 0], [58, 58]]],
            ),
            (
                "wwmf",
                [datetime(2023, 3, 1, 23, 0, 0), datetime(2023, 4, 1, 4, 0, 0)],
                [[[58, 58], [58, 0]], [[58, 58], [58, 58]]],
            ),
            (
                "w1",
                [datetime(2023, 3, 1, 23, 30, 0), datetime(2023, 5, 1, 15, 0, 0)],
                [[[13, 13], [13, 13]], [[0, 0], [0, 0]]],
            ),
            # Code replacement test with nebulosity
            # Test of code with nebulosity replacement
            (
                "wwmf",
                [datetime(2023, 3, 1), datetime(2023, 3, 2)],
                [[[72, 72], [72, 72]], [[0, 0], [0, 0]]],
            ),
            (
                "wwmf",
                [datetime(2023, 3, 1), datetime(2023, 3, 2)],
                [[[73, 73], [73, 73]], [[0, 0], [0, 0]]],
            ),
            (
                "wwmf",
                [datetime(2023, 3, 1), datetime(2023, 3, 2)],
                [[[0, 78], [0, 78]], [[0, 0], [78, 78]]],
            ),
            (
                "wwmf",
                [datetime(2023, 3, 1), datetime(2023, 3, 2)],
                [[[82, 82], [82, 0]], [[0, 82], [0, 0]]],
            ),
            (
                "wwmf",
                [datetime(2023, 3, 1), datetime(2023, 3, 2)],
                [[[83, 83], [83, 83]], [[0, 0], [0, 0]]],
            ),
        ],
    )
    def test_1_ts(self, units, valid_times, codes, assert_equals_result):
        """
        This test ensures that the good isolated phenomenon are excluded
        The threshold (50%) is bigger in order to see the exclusions
        """

        altitude = [[1045, 1501], [2040, 2509]]

        # to avoid that the phenomenon is over all the period
        valid_times.append(valid_times[-1] + Timedelta(hours=1))
        codes.append([[0, 0], [0, 0]])

        # We change the requiredDT and requiredDHmax to be able to see the exclusion
        assert_equals_result(
            self._compute(
                codes=codes,
                units=units,
                valid_times=valid_times,
                altitude=altitude,
                requiredDT=0.3,
                requiredDHmax=0.5,
            )
        )

    @pytest.mark.parametrize(
        "units,codes",
        [
            # 2TS with different families
            ("wwmf", (50, 31)),
            ("w1", (3, 9)),
            # Localisation with snow
            ("wwmf", (31, 60)),
            ("w1", (13, 2)),
            ("wwmf", (62, 63)),
            ("w1", (16, 17)),
        ],
    )
    def test_2_ts_different_families(self, units, codes, assert_equals_result):
        """
        This test handles simple cases with 2 TS over 2 valid_times
        """
        valid_times = [datetime(2023, 3, 1), datetime(2023, 3, 2), datetime(2023, 3, 3)]
        altitude = [[1070], [2099]]

        lon, lat = [40], [35, 36]
        codes = [
            [[codes[0]], [codes[0]]],
            [[codes[1]], [codes[1]]],
            [[0], [0]],  # to avoid that the phenomenon is over all the period
        ]
        assert_equals_result(
            self._compute(
                codes=codes,
                lon=lon,
                lat=lat,
                units=units,
                valid_times=valid_times,
                altitude=altitude,
            )
        )

    @pytest.mark.parametrize(
        "units,codes,durations",
        [
            # 2 TS not severe with 2 (<3) hours of covering and
            # 0.2 (<0.25) proportion of coverage => 2 distinct TS
            ("wwmf", (70, 61), (10, 2, 10)),
            ("w1", (2, 6), (10, 2, 10)),
            # 2 TS not severe with 4 (>3) hours of covering and
            # 0.2 (<0.25) proportion of coverage => 2 distinct TS
            ("wwmf", (70, 61), (20, 4, 20)),
            ("w1", (2, 6), (20, 4, 20)),
            # 2 TS not severe with 2 (<3) hours of covering and
            # 0.5 (>0.25) proportion of coverage => 2 distinct TS
            ("wwmf", (70, 61), (4, 2, 4)),
            ("w1", (2, 6), (4, 2, 4)),
            # 2 TS not severe with 4 (>3) hours of covering and
            # 0.4 (>0.25) proportion of coverage => same TS
            ("wwmf", (70, 61), (10, 4, 10)),
            ("w1", (2, 6), (10, 4, 10)),
            # 2 precipitation TS which 1 severe with 0.4 (>0.25) proportion of
            # intersection  => 2 distinct TS
            # Notice that if it was not severe it would consider as same TS
            ("wwmf", (70, 98), (10, 4, 10)),
            # 2 precipitation TS which 1 severe with 0.78 (>0.75) proportion of
            # intersection  => same TS
            ("wwmf", (70, 98), (1, 7, 1)),
        ],
    )
    def test_2_ts_same_families(self, units, codes, durations, assert_equals_result):
        """
        This test handles 2 TS  with valid_times which duration is given.
        The first and second period lasts duration[0] and the third one duration[1]
        """
        d0 = datetime(2023, 3, 1)
        valid_times = [
            d0,
            d0 + timedelta(hours=durations[0]),
            d0 + timedelta(hours=durations[0] + durations[1]),
            d0 + timedelta(hours=durations[0] + durations[1] + durations[2]),
        ]

        lon, lat = [40], [35, 36]
        codes = [
            [[0], [0]],
            [[codes[0]], [codes[0]]],
            [[codes[0]], [codes[1]]],
            [[codes[1]], [codes[1]]],
        ]
        assert_equals_result(
            self._compute(
                codes=codes, lon=lon, lat=lat, units=units, valid_times=valid_times
            )
        )

    @pytest.mark.parametrize(
        "codes,durations",
        [
            # 3 visibility TS
            ((30, 32, 33), (1, 4)),
            ((30, 32, 33), (4, 1)),
            # 3 precipitation TS with 2 subfamily
            ((51, 52, 60), (1, 4)),
            ((51, 58, 70), (4, 1)),
            # 3 precipitation TS with 1 subfamily
            ((51, 52, 53), (1, 4)),
            ((61, 62, 63), (4, 1)),
            ((70, 71, 77), (1, 4)),
            # 3 precipitation TS with 2 precipitations + 1 visibility
            ((32, 71, 77), (1, 4)),
            ((32, 70, 61), (4, 1)),
            ((71, 32, 77), (1, 4)),
            # 3 precipitation TS with 2 visibilities + 1 precipitation
            ((32, 33, 77), (4, 1)),
            ((32, 30, 61), (1, 4)),
            ((32, 77, 33), (4, 1)),
            # Phenomenon which can't be grouped by pair (according to their temporality)
            ((51, 71, 52), (2, 2)),
        ],
    )
    def test_3_ts_temporalities(self, codes, durations, assert_equals_result):
        """This test handles 3 phenomenon with two of same temporality
        to ensure that they will be well put together"""
        valid_times = [
            datetime(2023, 3, 1, 0),
            datetime(2023, 3, 1, 3),
            datetime(2023, 3, 1, 3 + durations[0]),
            datetime(2023, 3, 1, 3 + durations[0] + durations[1]),
            datetime(2023, 3, 1, 3 + durations[0] + durations[1] + 3),
        ]

        lon, lat = [40], [35, 36]
        codes = [
            [[0], [0]],
            [[codes[0]], [codes[0]]],
            [[codes[0]], [codes[1]]],
            [[codes[1]], [codes[2]]],
            [[codes[2]], [codes[2]]],
        ]

        assert_equals_result(
            self._compute(codes=codes, lon=lon, lat=lat, valid_times=valid_times)
        )

    @pytest.mark.parametrize(
        "codes",
        [
            # >3 visibility TS
            ([[[31, 32], [33, 38]], [[0, 0], [0, 0]]]),
            ([[[31, 32], [33, 38]], [[31, 39], [0, 0]]]),
            # 3 visibility TS and 1 precipitation
            ([[[31, 32], [33, 60]], [[0, 0], [0, 0]]]),
            # 2 visibility TS and 2 precipitation
            ([[[31, 61], [33, 60]], [[0, 0], [0, 0]]]),
            # 1 visibility TS and 3 precipitation
            ([[[31, 62], [63, 60]], [[0, 0], [0, 0]]]),
            # >3 precipitation TS and no severe
            ([[[51, 61], [70, 71]], [[0, 0], [0, 0]]]),
            ([[[51, 61], [70, 71]], [[80, 0], [0, 0]]]),
            ([[[51, 61], [70, 71]], [[80, 91], [0, 0]]]),
            ([[[51, 61], [70, 71]], [[80, 90], [70, 0]]]),
            (
                [[[51, 61], [70, 71]], [[80, 90], [50, 60]]]
            ),  # >3 precipitation TS and severe
            ([[[51, 61], [70, 71]], [[98, 0], [0, 0]]]),
            ([[[51, 61], [70, 71]], [[98, 99], [0, 0]]]),
            ([[[51, 61], [70, 84]], [[98, 71], [0, 85]]]),
            # several precipitation + visibility TS
            ([[[51, 32], [0, 0]], [[0, 0], [84, 92]]]),
            ([[[51, 32], [33, 71]], [[80, 0], [0, 0]]]),
            ([[[51, 32], [33, 71]], [[33, 91], [83, 92]]]),
            ([[[51, 32], [33, 71]], [[33, 91], [83, 38]]]),
            ([[[51, 32], [33, 71]], [[33, 91], [83, 98]]]),
            # If there is only 2 visibilities with 31 (Haze)
            # => the code and temporality of haze aren't included
            ([[[31, 32], [60, 61]], [[31, 0], [0, 0]]]),
            # If there is at least 3 visibilities with 31 (Haze)
            # => the temporality of haze isn't included
            ([[[31, 32], [33, 61]], [[31, 60], [0, 0]]]),
            ([[[31, 32], [33, 38]], [[31, 60], [61, 0]]]),
        ],
    )
    def test_more_than_3_ts_temporalities(self, codes, assert_equals_result):
        valid_times = [
            datetime(2023, 3, 1),
            datetime(2023, 3, 2),
            datetime(2023, 3, 3),
        ]

        # to avoid that the phenomenon is over all the period
        codes.append(
            [
                [0, 0],
                [0, 0],
            ]
        )
        assert_equals_result(self._compute(codes=codes, valid_times=valid_times))


class TestWeatherIntegration:
    inputs_dir: Path = Path(__file__).parent / "inputs" / "text_TS"

    @pytest.mark.parametrize(
        "period",
        ["20230309", "20230319", "20230321", "20230401", "20231102"],
    )
    @patch(
        "mfire.composite.weather.TEXT_ALGO",
        {
            "weather": {
                "generic": {
                    "params": {
                        "wwmf": {"field": "WWMF__SOL", "default_units": "Code WWMF"}
                    }
                }
            }
        },
    )  # this patch avoids to have to use all (useless) data files
    def test_generated_text(self, period: str, assert_equals_result):
        config = JsonFile(self.inputs_dir / f"prod_task_config_{period}.json").load()

        # Replace "test_data_dir" by appropriate values
        data: dict = recursive_format(
            config,
            values={
                "test_data_dir": str(self.inputs_dir),
            },
        )

        result = {}
        for value in data.values():
            component = TextComponentComposite(**value["components"][0])
            for geo_id in component.geos:
                text_manager = TextManager(component=component)
                generated_text = text_manager.compute(geo_id=geo_id)
                result[f"{component.name} > {geo_id}"] = "\n".join(
                    generated_text.split("\n")[1:]
                )

        assert_equals_result(result)

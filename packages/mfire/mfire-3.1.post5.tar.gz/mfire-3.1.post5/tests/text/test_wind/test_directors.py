from __future__ import annotations

import re
from pathlib import Path
from typing import Optional
from unittest.mock import patch

import numpy as np
import pytest

from mfire.text.wind.base import BaseParamBuilder
from mfire.text.wind.builders import GustParamBuilder, WindParamBuilder
from mfire.text.wind.directors import WindDirector
from mfire.text.wind.reducers.gust_summary_builder.gust_enum import GustCase
from mfire.text.wind.reducers.wind_summary_builder.helpers import WindCase
from tests.text.utils import generate_valid_times

from .factories import CompositeFactory1x1

FILE_PATH: Path = Path("unit_test_synthesis.txt")
FILE_PATH.unlink(missing_ok=True)


class TestDirectorsForOneParam:
    """TestDirectorsForOneParam class."""

    COMPOSITE_FACTORY: CompositeFactory1x1 = CompositeFactory1x1
    EXCLUDED_SUMMARY_KEYS: dict[str, list[str]] = {
        WindParamBuilder.PARAM_NAME: [
            WindParamBuilder.EXTRA_KEY,
            "fingerprint_raw",
            "fingerprint_filtered",
            "fingerprint_blocks",
        ]
    }
    BUILDERS: list[BaseParamBuilder] = [GustParamBuilder, WindParamBuilder]
    TESTED_BUILDER: BaseParamBuilder = None

    @classmethod
    def _get_fakes_builder(cls) -> BaseParamBuilder:
        """Get builder which needs to be faked."""
        for builder in cls.BUILDERS:
            if builder != cls.TESTED_BUILDER:
                return builder

    @classmethod
    def print_title_in_file(cls, title: str):
        with open(FILE_PATH, "a") as f:
            out: str = f"# {title}:"
            f.write(f"\n{out}\n{len(out) * '-'}\n\n")

    @classmethod
    def _print_text_synthesis_in_file(cls, case_value: Optional[str], text: str):
        with open(FILE_PATH, "a") as f:
            if case_value is not None:
                res = re.match(".*_([0-9]*)$", case_value)
                case_short: str = res.group(1)
                f.write(f"cas {case_short}:\n{text}\n\n")
            else:
                f.write(f"{text}\n\n")

    def _check(
        self, valid_times, data_gust, data_wf, data_wd, case_exp, assert_equals_result
    ):
        """Check directors process by testing wind data, produced summary and text."""
        # Get or set data
        if data_gust is None:
            data_gust = [0.0] * len(data_wf)
        elif data_wf is None and data_wd is None:
            data_wf = [0.0] * len(data_gust)
            data_wd = [np.nan] * len(data_gust)
        else:
            raise ValueError("Bad input arguments !")

        # Create composite
        composite = self.COMPOSITE_FACTORY.get_composite_when_term_data_is_one_number(
            valid_times=valid_times,
            data_wind=data_wf,
            data_dir=data_wd,
            data_gust=data_gust,
        )

        # Create director
        director: WindDirector = WindDirector()

        # Run director
        text: str = director.compute(geo_id="", composite=composite)

        # Check WindCaseNbr
        param_summary = director.reducer.summary["params"][
            self.TESTED_BUILDER.PARAM_NAME
        ]
        case_value: str = param_summary[self.TESTED_BUILDER.SELECTOR_KEY]
        assert case_value == case_exp.value

        # Check text
        assert_equals_result(text)

        self._print_text_synthesis_in_file(case_exp.value, text)


class TestGustDirectorsCase1(TestDirectorsForOneParam):
    """TestGustDirectorsCase1 class."""

    TESTED_BUILDER = GustParamBuilder

    @classmethod
    def setup_class(cls):
        cls.print_title_in_file("Gust Case 1")

    @pytest.mark.parametrize(
        "valid_times, data_gust",
        [
            (
                # No gust
                generate_valid_times(periods=12),
                [0.0] * 5 + [np.nan] + [0.0] * 6,
            ),
            (
                # All gust < 50 km/h
                generate_valid_times(periods=12),
                [2.0] * 12,
            ),
        ],
    )
    def test(self, valid_times, data_gust, assert_equals_result):
        """Test function which call _check method."""
        self._check(
            valid_times,
            data_gust,
            None,
            None,
            GustCase.CASE_1,
            assert_equals_result,
        )


class TestGustDirectorsCase2(TestDirectorsForOneParam):
    """TestGustDirectorsCase2 class."""

    TESTED_BUILDER = GustParamBuilder

    @classmethod
    def setup_class(cls):
        cls.print_title_in_file("Gust Case 2")

    @pytest.mark.parametrize(
        "valid_times, data_gust",
        [
            (
                # Gust terms: 2 2 50.1 70 70 70 70 70 70 2 2 2
                generate_valid_times(periods=12),
                [2.0] * 2 + [50.1] + [70.0] * 6 + [2.0] * 3,
            ),
            (
                # Gust terms: 70 70 70 70 70 70 70 70 70 70 70 70
                generate_valid_times(periods=12),
                [70.0] * 12,
            ),
            (
                # Gust terms: 2 2 80 80 40 70 70 70 70 2 2 2
                generate_valid_times(periods=12),
                [2.0] * 2 + [80] * 2 + [40.0] + [70] * 4 + [2.0] * 3,
            ),
            (
                # Gust terms: 2 2 70 70 40 40 70 70 70 2 2 2
                generate_valid_times(periods=12),
                [2.0] * 2 + [70] * 2 + [40.0] * 2 + [70] * 3 + [2.0] * 3,
            ),
            (
                # Gust terms: 2 2 70 70 40 40 40 70 70 70 2 2
                generate_valid_times(periods=12),
                [2.0] * 2 + [70] * 2 + [40.0] * 3 + [70] * 3 + [2.0] * 2,
            ),
            (
                # Gust terms: 2 2 2 70 40 40 40 70 80 70 2 2
                generate_valid_times(periods=12),
                [2.0] * 3 + [70] + [40.0] * 3 + [70] + [80] + [70] + [2.0] * 2,
            ),
            (
                # Gust terms: 2 2 2 90 2 2 2 2 70 70 70 2
                generate_valid_times(periods=12),
                [2.0] * 3 + [90] + [2.0] * 4 + [70] * 3 + [2.0],
            ),
            (
                # Gust terms: 2 2 70 70 2 2 2 2 70 70 70 2
                generate_valid_times(periods=12),
                [2.0] * 2 + [70] * 2 + [2.0] * 4 + [70] * 3 + [2.0],
            ),
            (
                # Gust terms: 11 70 70 70 2 2 2 2 70 70 70 2
                generate_valid_times(periods=12),
                [11.0] + [70] * 3 + [2.0] * 4 + [70] * 3 + [2.0],
            ),
            (
                # Gust terms: 70 70 70 70 2 2 2 2 90 70 70 70
                generate_valid_times(periods=12),
                [70] * 4 + [2.0] * 4 + [90] + [70] * 3,
            ),
            (
                # Gust terms: 2 2 70 40 70 2 2 2 2 2 2 2
                generate_valid_times(periods=12),
                [2.0] * 2 + [70] + [40] + [70] + [2.0] * 7,
            ),
            (
                # Gust terms: 2 2 70 40 40 70 2 2 2 2 2 2
                generate_valid_times(periods=12),
                [2.0] * 2 + [70] + [40] * 2 + [70] + [2.0] * 6,
            ),
            (
                # Gust terms: 2 2 70 40 40 40 70 2 2 2 2 2
                generate_valid_times(periods=12),
                [2.0] * 2 + [70] + [40] * 3 + [70] + [2.0] * 5,
            ),
            (
                # Gust terms: 2 2 60 40 40 40 40 90 2 2 2 2
                generate_valid_times(periods=12),
                [2.0] * 2 + [60] + [40] * 4 + [90] + [2.0] * 4,
            ),
            (
                # Gust terms: 40 55 40 40 40 40 40 40 40 40 60 40 40 40 40 40 40 40 4
                # 0 40 40 80 40 40
                generate_valid_times(periods=24),
                [40] + [55] + [40] * 8 + [60] + [40] * 10 + [80] + [40] * 2,
            ),
            (
                # Gust terms: 60 40 40 40 40 40 40 40 40 40 40 90
                generate_valid_times(periods=12),
                [60] + [40] * 10 + [90],
            ),
            (
                # Gust terms: 2 2 60 40 40 40 40 90 90 2 2 2
                generate_valid_times(periods=12),
                [2.0] * 2 + [60] + [40] * 4 + [90] * 2 + [2.0] * 3,
            ),
            (
                # Gust terms: 2 2 60 40 40 40 40 90 90 2 2 2
                generate_valid_times(periods=12),
                [2.0] + [70] + [60] + [40] * 4 + [90] * 2 + [2.0] * 3,
            ),
            (
                # Gust terms: 2 60 60 60 40 40 40 40 70 70 70 40 40 40 40 80 80 80 2
                # 2 2 2 2 2
                generate_valid_times(periods=24),
                [2.0] + [60] * 3 + [40] * 4 + [70] * 3 + [40] * 4 + [80] * 3 + [2] * 6,
            ),
            (
                # Gust terms: 2 60 60 60 40 40 40 40 70 70 70 40 40 40 40 80 80 80 2
                # 2 2 2 90 2
                generate_valid_times(periods=24),
                [2.0]
                + [60] * 3
                + [40] * 4
                + [70] * 3
                + [40] * 4
                + [80] * 3
                + [2] * 4
                + [90]
                + [2],
            ),
            (
                # Gust terms: 60 60 60 60 40 40 40 40 70 70 70 40 40 40 40 80 80 80 80
                # 80 80 80 80 80
                generate_valid_times(periods=24),
                [60] * 4 + [40] * 4 + [70] * 3 + [40] * 4 + [80] * 9,
            ),
            (
                # Gust terms: 60 60 60 60 40 40 40 40 70 70 70 40 40 40 40 90 40 40 40
                # 40 80 80 80 2
                generate_valid_times(periods=24),
                [60] * 4
                + [40] * 4
                + [70] * 3
                + [40] * 4
                + [90]
                + [40] * 4
                + [80] * 3
                + [2],
            ),
            (
                # Gust terms: 40 55 55 40 40 40 40 40 40 40 60 60 60 40 40 40 40 70 40
                # 40 40 40  80 80
                generate_valid_times(periods=24),
                [40]
                + [55] * 2
                + [40] * 7
                + [60] * 3
                + [40] * 4
                + [70]
                + [40] * 4
                + [80] * 2,
            ),
            (
                # Gust terms: 60 60 60 60 40 40 40 70 70 70 70 40 40 90 90 90 40 40 40
                # 40 80 80 80 2
                generate_valid_times(periods=24),
                [60] * 4
                + [40] * 3
                + [70] * 4
                + [40.0] * 2
                + [90] * 3
                + [40] * 4
                + [80.0] * 3
                + [2],
            ),
        ],
    )
    def test(self, valid_times, data_gust, assert_equals_result):
        """Test function which call _check method."""
        self._check(
            valid_times,
            data_gust,
            None,
            None,
            GustCase.CASE_2,
            assert_equals_result,
        )


class TestWindDirectors(TestDirectorsForOneParam):
    """TestWindDirectors class."""

    TESTED_BUILDER = WindParamBuilder


class TestDirectorsWindCase1(TestWindDirectors):
    """Test Directors for case 1."""

    @classmethod
    def setup_class(cls):
        cls.print_title_in_file("Wind Case 1")

    @pytest.mark.parametrize(
        "valid_times, data_wf, data_wd",
        [
            (
                # type 1 terms (Case 1)
                generate_valid_times(periods=3),
                [10.0, 11.0, 12.0],
                [0.1, 1.0, 2.0],
            )
        ],
    )
    def test(
        self,
        valid_times,
        data_wf,
        data_wd,
        assert_equals_result,
    ):
        """Test function which call _check method."""
        self._check(
            valid_times,
            None,
            data_wf,
            data_wd,
            WindCase.CASE_1,
            assert_equals_result,
        )


class TestDirectorsWindCase2(TestWindDirectors):
    """TestDirectorsWindCase2 class.

    Test Directors for case 2.
    """

    @classmethod
    def setup_class(cls):
        cls.print_title_in_file("Wind Case 2")

    @pytest.mark.parametrize(
        "valid_times, data_wf, data_wd",
        [
            (
                # Type 2 terms (Case 2):
                # All terms have a wind direction but there is not a common direction
                generate_valid_times(periods=3),
                [15.0, 16.0, 20.0],
                [0.1, 180.0, 250.0],
            ),
            (
                # Type 1 and 2 terms (Case 2):
                # But there are not enough term to build a common wind direction period
                # (we need at least 3 type 2 terms).
                generate_valid_times(periods=3),
                [1.0, 16.0, 20.0],
                [np.nan, 180.0, 250.0],
            ),
            (
                # Type 2 terms (Case 2):
                # All terms have a wind direction but there is not a common direction
                generate_valid_times(periods=3),
                [15.0, 16.0, 20.0],
                [0.1, 20.0, 190.0],
            ),
            (
                # Type 2 terms (Case 2):
                # The first 3 terms has a common wind direction but the last term
                # has no wind direction. So no wind direction period found.
                generate_valid_times(periods=4),
                [15.0, 16.0, 20.0, 21.0],
                [20.0, 20.0, 20.0, np.nan],
            ),
            (
                # Type 2 terms (Case 2):
                # same WindDirection in the 1st and the last WindDirectionPeriod
                generate_valid_times(periods=10),
                [15.0] * 10,
                [0.1] * 4 + [157.6] * 2 + [0.1] * 4,
            ),
            (
                # Type 2 terms (Case 2):
                # the 1st and the last WindDirection are opposite
                generate_valid_times(periods=10),
                [15.0] * 10,
                [180.0] * 4 + [157.6] * 2 + [0.1] * 4,
            ),
            (
                # Only type 2 terms with the direction 270 (Case 2)
                # So There is a common wind direction: 270 ie 'Ouest'
                generate_valid_times(periods=3),
                [15.0, 16.0, 20.0],
                [270.0, 270.0, 270.0],
            ),
            (
                # Type 1 and 2 (Case 2)
                # All terms 2 have a wind direction which is 'Ouest'. So There is a
                # common wind direction: 270 ie 'Ouest'
                generate_valid_times(periods=4),
                [15.0, 16.0, 20.0, 1.0],
                [270.0, 270.0, 270.0, np.nan],
            ),
            (
                # Type 2 terms (Case 2)
                # All terms 2 have a wind direction.
                # There are 3 common direction periods:
                # - period 0: term 0 to 2 with 0 direction ie 'Nord'
                # - period 1: term 3 to 5 with 160 direction ie 'Sud-Sud-Est'
                # - period 2: term 6 to 8 with 320 direction ie 'Nord-Ouest'
                generate_valid_times(periods=9),
                [15.0, 16.0, 20.0, 15.0, 16.0, 20.0, 15.0, 16.0, 20.0],
                [0.1] * 3 + [160.0] * 3 + [320.0] * 3,
            ),
            (
                # Type 1 and 2 terms (Case 2)
                # All terms 2 have a wind direction.
                # There are 3 common direction periods:
                # - period 0: term 0 to 2 with 0 direction ie 'Nord'
                # - period 1: term 3 to 5 with 160 direction ie 'Sud-Sud-Est'
                # - period 2: term 6 to 8 with 320 direction ie 'Nord-Ouest'
                generate_valid_times(periods=10),
                [15.0, 16.0, 20.0, 15.0, 16.0, 20.0, 15.0, 16.0, 20.0, 1.0],
                [0.1] * 3 + [160.0] * 3 + [320.0] * 3 + [np.nan],
            ),
        ],
    )
    def test(
        self,
        valid_times,
        data_wf,
        data_wd,
        assert_equals_result,
    ):
        """Test function which call _check method."""
        self._check(
            valid_times,
            None,
            data_wf,
            data_wd,
            WindCase.CASE_2,
            assert_equals_result,
        )


class TestDirectorsWindCase31Block(TestWindDirectors):
    """TestDirectorsWindCase31Block class

    Test Directors for case 3 with 1 block.
    """

    @classmethod
    def setup_class(cls):
        cls.print_title_in_file("Wind Case 3 (1 block)")

    @pytest.mark.parametrize(
        "valid_times, data_wf, data_wd, case_exp",
        [
            (
                # Case 3_1B
                # - 1 wind force period: 30 km/h wind force
                # - 1 wind direction period: 0.1° (sympo code 0)
                generate_valid_times(periods=3),
                [30.0, 30.0, 30.0],
                [0.1] * 3,
                WindCase.CASE_3_1B_1,
            ),
            (
                # Case 3_1B_2
                # - 1 wind force period: 30 km/h wind force
                # - 2 wind direction period: 0.1° and 4° (0 and 8 sympo codes)
                generate_valid_times(periods=6),
                [30.0] * 6,
                [0.1] * 3 + [157.5] * 3,
                WindCase.CASE_3_1B_2,
            ),
            (
                # Case 3_1B_3
                # Only type 3 terms:
                # - without wind direction
                # - all terms has a 30 km/h wind force
                generate_valid_times(periods=3),
                [30.0, 30.0, 30.0],
                [np.nan, np.nan, np.nan],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Case CASE_3_1B_3
                # Input Fingerprint: 222222223223222222222222
                # 2 type 3 terms with the max wind force for each of us
                generate_valid_times(periods=24),
                [15.0] * 8 + [30.0] * 1 + [15.0] * 2 + [30.0] * 1 + [15.0] * 12,
                [np.nan] * 24,
                WindCase.CASE_3_1B_3,
            ),
            (
                # Case 3_1B_4: 2 not juxtaposed force intervals WF1 < WF2
                # - 2 not juxtaposed wind force periods: 30 km/h and 40 km/h
                # - 1 wind direction period: 0.1° (sympo code 0)
                generate_valid_times(periods=6),
                [30.0, 30.0, 30.0, 40.0, 40.0, 40.0],  # WF1 < WF2
                [0.1] * 6,
                WindCase.CASE_3_1B_4,
            ),
            (
                # Case 3_1B_4: 2 not juxtaposed force intervals WF1 > WF2
                # - 2 not juxtaposed wind force periods: 30 km/h and 40 km/h
                # - 1 wind direction period: 0.1° (sympo code 0)
                generate_valid_times(periods=6),
                [40.0, 40.0, 40.0, 30.0, 30.0, 30.0],  # WF1 > WF2
                [0.1] * 6,
                WindCase.CASE_3_1B_4,
            ),
            (
                # Case 3_1B_5: juxtaposed force intervals WF1 + 5 = WF2
                # - 2 not juxtaposed wind force periods: 30 km/h and 35 km/h
                # - 1 wind direction period: 0.1° (sympo code 0)
                generate_valid_times(periods=6),
                [30.0, 30.0, 30.0, 35.0, 35.0, 35.0],  # WF1 < WF2
                [0.1] * 6,
                WindCase.CASE_3_1B_5,
            ),
            (
                # Case 3_1B_5: juxtaposed force intervals WF1 = WF2 + 5
                # - 2 not juxtaposed wind force periods: 35 km/h and 30 km/h
                # - 1 wind direction period: 0.1° (sympo code 0)
                generate_valid_times(periods=6),
                [35.0, 35.0, 35.0, 30.0, 30.0, 30.0],  # WF1 > WF2
                [0.1] * 6,
                WindCase.CASE_3_1B_5,
            ),
            (
                # Case 3_1B_6
                # - 2 not juxtaposed wind force periods WF1 < WF2
                # - 2 wind direction period: 0.1° and 180°
                # wf and wd changes are not simultaneous
                generate_valid_times(periods=7),
                [30.0, 30.0, 30.0, 40.0, 40.0, 40.0, 40.0],  # WF1 < WF2
                [0.1] * 4 + [157.6] * 3,
                WindCase.CASE_3_1B_6,
            ),
            (
                # Case 3_1B_6
                # - 2 not juxtaposed wind force periods WF1 > WF2
                # - 2 wind direction period: 0.1° and 180°
                # wf and wd changes are not simultaneous
                generate_valid_times(periods=7),
                [40.0, 40.0, 40.0, 30.0, 30.0, 30.0, 30.0],  # WF1 < WF2
                [0.1] * 4 + [157.6] * 3,
                WindCase.CASE_3_1B_6,
            ),
            (
                # Case 3_1B_7
                # - 2 not juxtaposed wind force periods WF1 < WF2
                # - 2 wind direction period: 0.1° and 180°
                # wf and wd changes are simultaneous
                generate_valid_times(periods=7),
                [30.0, 30.0, 30.0, 30.0, 40.0, 40.0, 40.0],  # WF1 < WF2
                [0.1] * 4 + [157.6] * 3,
                WindCase.CASE_3_1B_7,
            ),
            (
                # Case 3_1B_7
                # - 2 not juxtaposed wind force periods WF1 > WF2
                # - 2 wind direction period: 0.1° and 180°
                # wf and wd changes are simultaneous
                generate_valid_times(periods=7),
                [40.0, 40.0, 40.0, 40.0, 30.0, 30.0, 30.0],  # WF1 > WF2
                [0.1] * 4 + [157.6] * 3,
                WindCase.CASE_3_1B_7,
            ),
            (
                # Case 3_1B_8
                # - 2 juxtaposed wind force periods WF1 < WF2
                # - 2 wind direction period: 0.1° and 180°
                # wf and wd changes are simultaneous
                generate_valid_times(periods=7),
                [30.0, 30.0, 30.0, 30.0, 35.0, 35.0, 35.0],  # WF1 < WF2
                [0.1] * 4 + [157.6] * 3,
                WindCase.CASE_3_1B_8,
            ),
            (
                # Case 3_1B_8
                # - 2 juxtaposed wind force periods WF1 > WF2
                # - 2 wind direction period: 0.1° and 180°
                # wf and wd changes are simultaneous
                generate_valid_times(periods=7),
                [35.0] * 4 + [30.0] * 3,  # WF1 > WF2
                [0.1] * 4 + [157.6] * 3,
                WindCase.CASE_3_1B_8,
            ),
            (
                # Case 3_1B_9
                # - 2 not juxtaposed wind force periods WF1 < WF2
                # - no wind direction period
                # wf and wd changes are simultaneous
                generate_valid_times(periods=4),
                [30.0] * 2 + [40.0] * 2,  # WF1 < WF2
                [0.1] * 2 + [np.nan] * 2,
                WindCase.CASE_3_1B_9,
            ),
            (
                # Case 3_1B_9
                # - 2 not juxtaposed wind force periods WF1 > WF2
                # - no wind direction period
                # wf and wd changes are simultaneous
                generate_valid_times(periods=4),
                [40.0] * 2 + [30.0] * 2,  # WF1 > WF2
                [0.1] * 2 + [np.nan] * 2,
                WindCase.CASE_3_1B_9,
            ),
            (
                # Case CASE_3_1B_9
                # Input Fingerprint: 222222223223222222222222
                # 2 type 3 terms: the max wind force is on the second term
                generate_valid_times(periods=24),
                [15.0] * 8 + [30.0] * 1 + [15.0] * 2 + [40.0] * 1 + [15.0] * 12,
                [np.nan] * 24,
                WindCase.CASE_3_1B_9,
            ),
            (
                # Case CASE_3_1B_9
                # Input Fingerprint: 222222223223222322222222
                # 3 type 3 terms: the max wind force is on the second and the third term
                generate_valid_times(periods=24),
                [15.0] * 8
                + [30.0] * 1
                + [15.0] * 2
                + [40.0] * 1
                + [15.0] * 3
                + [40.0] * 1
                + [15.0] * 8,
                [np.nan] * 24,
                WindCase.CASE_3_1B_9,
            ),
            (
                # Case 3_1B_10
                # - 2 juxtaposed wind force periods WF1 < WF2
                # - no wind direction period
                # wf and wd changes are simultaneous
                generate_valid_times(periods=4),
                [30.0, 30.0, 35.0, 35.0],  # WF1 < WF2
                [0.1] * 2 + [np.nan] * 2,
                WindCase.CASE_3_1B_10,
            ),
            (
                # Case 3_1B_10
                # - 2 juxtaposed wind force periods WF1 > WF2
                # - no wind direction period
                # wf and wd changes are simultaneous
                generate_valid_times(periods=4),
                [35.0, 35.0, 30.0, 30.0],  # WF1 > WF2
                [0.1] * 2 + [np.nan] * 2,
                WindCase.CASE_3_1B_10,
            ),
            (
                # Case 3_1B_11
                # - variable wind forces: 3 wf periods 35km/h, 50 km/h, 40 km/h
                # - 1 wind direction period
                # wf and wd changes are simultaneous
                generate_valid_times(periods=3),
                [39.0, 46.0, 40.0],
                [0.1] * 3,
                WindCase.CASE_3_1B_11,
            ),
            (
                # Case 3_1B_12
                # - variable wind forces: 6 wf periods
                # - 2 wind direction periods
                # wf and wd changes are simultaneous
                generate_valid_times(periods=6),
                [39.0, 46.0, 40.0, 39.0, 46.0, 40.0],
                [0.1] * 3 + [157.5] * 3,
                WindCase.CASE_3_1B_12,
            ),
            (
                # Case 3_1B_13
                # - variable wind forces: 3 wf periods 35km/h, 45 km/h, 40 km/h
                # - no wind direction period
                # wf and wd changes are simultaneous
                generate_valid_times(periods=3),
                [39.0, 46.0, 40.0],
                [0.1, 180.0, np.nan],
                WindCase.CASE_3_1B_13,
            ),
        ],
    )
    def test_one_type3_block(
        self,
        valid_times,
        data_wf,
        data_wd,
        case_exp: WindCase,
        assert_equals_result,
    ):
        """Test when there is 1 type 3 WIndBlock."""
        self._check(
            valid_times,
            None,
            data_wf,
            data_wd,
            case_exp,
            assert_equals_result,
        )


class TestDirectorsWindCase32Blocks(TestWindDirectors):
    """TestDirectorsWindCase32Blocks class.

    Test Directors for case 3 with 2 blocks.
    """

    @classmethod
    def setup_class(cls):
        cls.print_title_in_file("Wind Case 3 (2 blocks)")

    @pytest.mark.parametrize(
        "valid_times, data_wf, data_wd, case_exp",
        [
            (
                # Case 3_2B_1
                # Input Fingerprint: 333333322222222333333333
                # - WF0 = WF1 = 30 km/h
                # - WD0 = WD1 = 0.1° (sympo code 0)
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [30.0] * 9,
                [0.1] * 24,
                WindCase.CASE_3_2B_1,
            ),
            (
                # Case 3_2B_2
                # Input Fingerprint: 333333322222222333333333
                # - WF0 = WF1 = 30 km/h
                # - WD0 = 0.1° != WD1 = 90°
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [30.0] * 9,
                [0.1] * 7 + [np.nan] * 8 + [90.0] * 9,
                WindCase.CASE_3_2B_2,
            ),
            (
                # Case 3_2B_3
                # Input Fingerprint: 333333322222222333333333
                # - WF0 = WF1 = 30 km/h
                # - WD0 = 0.1°, no WD1
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [30.0] * 9,
                [0.1] * 7 + [np.nan] * 17,
                WindCase.CASE_3_2B_3,
            ),
            (
                # Case 3_2B_4
                # Input Fingerprint: 333333322222222333333333
                # - WF0 = WF1 = 30 km/h
                # - no WD0, WD1 = 0.1°
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [30.0] * 9,
                [np.nan] * 15 + [0.1] * 9,
                WindCase.CASE_3_2B_4,
            ),
            (
                # Case 3_2B_5
                # Input Fingerprint: 333333322222222333333333
                # - WF0 = WF1 = 30 km/h
                # - WD00, WD01 and WD1
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [30.0] * 9,
                [0.1] * 4 + [136.0] * 3 + [np.nan] * 8 + [271.0] * 9,
                WindCase.CASE_3_2B_5,
            ),
            (
                # Case 3_2B_6
                # Input Fingerprint: 333333322222222333333333
                # - WF0 = WF1 = 30 km/h
                # - WD00, WD01 and no WD1
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [30.0] * 9,
                [0.1] * 4 + [136.0] * 3 + [np.nan] * 17,
                WindCase.CASE_3_2B_6,
            ),
            (
                # Case 3_2B_7
                # Input Fingerprint: 333333322222222333333333
                # - WF0 = WF1 = 30 km/h
                # - WD0, WD10 and WD1
                generate_valid_times(periods=24),
                [30.0] * 9 + [15.0] * 8 + [30.0] * 7,
                [271.0] * 9 + [np.nan] * 8 + [0.1] * 4 + [136.0] * 3,
                WindCase.CASE_3_2B_7,
            ),
            (
                # Case 3_2B_8
                # Input Fingerprint: 333333322222222333333333
                # - WF0 = WF1 = 30 km/h
                # - no WD00 and WD10, WD11
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [30.0] * 9,
                [np.nan] * 15 + [0.1] * 4 + [136.0] * 5,
                WindCase.CASE_3_2B_8,
            ),
            (
                # Case 3_2B_9
                # Input Fingerprint: 333333322222222333333333
                # - WF0 = WF1 = 30 km/h
                # - WD00, WD01 and WD10, WD11
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [30.0] * 9,
                [0.1] * 4 + [136.0] * 3 + [np.nan] * 8 + [22.5] * 4 + [158.0] * 5,
                WindCase.CASE_3_2B_9,
            ),
            (
                # Case 3_2B_10
                # Input Fingerprint: 333333322222222333333333
                # - WF0 = WF1 = 30 km/h
                # - no WD
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [30.0] * 9,
                [np.nan] * 24,
                WindCase.CASE_3_2B_10,
            ),
            (
                # Case 3_2B_12
                # Input Fingerprint: 333333322222222333333333
                # - WF0 30 km/h juxtaposed with WF1
                # - WD0 = WD1 = 0.1° (sympo code 0)
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [35.0] * 9,
                [0.1] * 24,
                WindCase.CASE_3_2B_12,
            ),
            (
                # Case 3_2B_14
                # Input Fingerprint: 333333322222222333333333
                # - WF0 30 km/h juxtaposed with WF1
                # - WD0 = 0.1° != WD1 = 90°
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [35.0] * 9,
                [0.1] * 7 + [np.nan] * 8 + [90.0] * 9,
                WindCase.CASE_3_2B_14,
            ),
            (
                # Case 3_2B_16
                # Input Fingerprint: 333333322222222333333333
                # - WF0 30 km/h juxtaposed with WF1
                # - WD0 = 0.1°, no WD1
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [35.0] * 9,
                [0.1] * 7 + [np.nan] * 17,
                WindCase.CASE_3_2B_16,
            ),
            (
                # Case 3_2B_18
                # Input Fingerprint: 333333322222222333333333
                # - WF0 30 km/h juxtaposed with WF1
                # - no WD0, WD1 = 0.1°
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [35.0] * 9,
                [np.nan] * 15 + [0.1] * 9,
                WindCase.CASE_3_2B_18,
            ),
            (
                # Case 3_2B_20
                # Input Fingerprint: 333333322222222333333333
                # - WF0 30 km/h juxtaposed with WF1
                # - WD00, WD01 and WD1
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [35.0] * 9,
                [0.1] * 4 + [136.0] * 3 + [np.nan] * 8 + [271.0] * 9,
                WindCase.CASE_3_2B_20,
            ),
            (
                # Case 3_2B_22
                # Input Fingerprint: 333333322222222333333333
                # - WF0 30 km/h juxtaposed with WF1
                # - WD00 , WD01 and no WD1
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [35.0] * 9,
                [0.1] * 3 + [136.0] * 4 + [np.nan] * 17,
                WindCase.CASE_3_2B_22,
            ),
            (
                # Case 3_2B_24
                # Input Fingerprint: 333333322222222333333333
                # - WF0 30 km/h juxtaposed with WF1
                # - WD0, WD10 and WD11
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [35.0] * 9,
                [271.0] * 7 + [np.nan] * 8 + [0.1] * 4 + [136.0] * 5,
                WindCase.CASE_3_2B_24,
            ),
            (
                # Case 3_2B_26
                # Input Fingerprint: 333333322222222333333333
                # - WF0 30 km/h juxtaposed with WF1
                # - no WD0 , WD10 and WD11
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [35.0] * 9,
                [np.nan] * 15 + [0.1] * 4 + [136.0] * 5,
                WindCase.CASE_3_2B_26,
            ),
            (
                # Case 3_2B_28
                # Input Fingerprint: 333333322222222333333333
                # - WF0 30 km/h juxtaposed with WF1
                # - WD0, WD1, WD10 and WD12
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [35.0] * 9,
                [0.1] * 4 + [136.0] * 3 + [np.nan] * 8 + [22.5] * 4 + [158.0] * 5,
                WindCase.CASE_3_2B_28,
            ),
            (
                # Case 3_2B_30
                # Input Fingerprint: 333333322222222333333333
                # - WF0 30 km/h juxtaposed with WF1
                # - no WD
                generate_valid_times(periods=24),
                [30.0] * 7 + [15.0] * 8 + [35.0] * 9,
                [np.nan] * 24,
                WindCase.CASE_3_2B_30,
            ),
        ],
    )
    def test_two_type3_blocks(
        self,
        valid_times,
        data_wf,
        data_wd,
        case_exp: WindCase,
        assert_equals_result,
    ):
        """Test when there are 2 type 3 WindBlocks."""
        self._check(
            valid_times,
            None,
            data_wf,
            data_wd,
            case_exp,
            assert_equals_result,
        )

    @pytest.mark.parametrize(
        "valid_times, data_wf, data_wd, case_exp",
        [
            (
                # Case 3_2B_11
                # Input Fingerprint: 333333333333333322223333
                # - WF0 != WF1 not juxtaposed
                # - WD0 = WD1 = 0.1° (sympo code 0)
                generate_valid_times(periods=24),
                [34.9] * 16 + [15.0] * 4 + [45.0] * 4,
                [0.1] * 24,
                WindCase.CASE_3_2B_11,
            ),
            (
                # Case 3_2B_13
                # Input Fingerprint: 333333333333333322223333
                # - WF0 != WF1 not juxtaposed
                # - WD0 = 0.1° and WD1 = 140°
                # WF and WD changes are not simultaneous
                generate_valid_times(periods=24),
                [34.9] * 16 + [15.0] * 4 + [45.0] * 4,
                [0.1] * 16 + [np.nan] * 4 + [140.0] * 4,
                WindCase.CASE_3_2B_13,
            ),
            (
                # Case 3_2B_15
                # Input Fingerprint: 333333333333333322223333
                # - WF0 != WF1 not juxtaposed
                # - WD0 = 0.1°, no WD1
                generate_valid_times(periods=24),
                [34.9] * 16 + [15.0] * 4 + [45.0] * 4,
                [0.1] * 16 + [np.nan] * 8,
                WindCase.CASE_3_2B_15,
            ),
            (
                # Case 3_2B_17
                # Input Fingerprint: 333333333333333322223333
                # - WF0 != WF1 not juxtaposed
                # - no WD0, WD1 = 0.1°
                generate_valid_times(periods=24),
                [34.9] * 16 + [15.0] * 4 + [45.0] * 4,
                [np.nan] * 20 + [0.1] * 4,
                WindCase.CASE_3_2B_17,
            ),
            (
                # Case 3_2B_19
                # Input Fingerprint: 333333333333333322223333
                # - WF0 != WF1 not juxtaposed
                # - WD00, WD01 and WD1
                generate_valid_times(periods=24),
                [34.9] * 16 + [15.0] * 4 + [45.0] * 4,
                [0.1] * 8 + [136.0] * 8 + [np.nan] * 4 + [271.0] * 4,
                WindCase.CASE_3_2B_19,
            ),
            (
                # Case 3_2B_21
                # Input Fingerprint: 333333333333333322223333
                # - WF0 != WF1 not juxtaposed
                # - WD00, WD01 and no WD1
                generate_valid_times(periods=24),
                [34.9] * 16 + [15.0] * 4 + [45.0] * 4,
                [0.1] * 8 + [136.0] * 8 + [np.nan] * 8,
                WindCase.CASE_3_2B_21,
            ),
            (
                # Case 3_2B_23
                # Input Fingerprint: 333333333333333322223333
                # - WF0 != WF1 not juxtaposed
                # - WD0, WD10 and WD12
                generate_valid_times(periods=24),
                [34.9] * 10 + [15.0] * 4 + [45.0] * 10,
                [0.1] * 10 + [np.nan] * 4 + [135.0] * 5 + [271.0] * 5,
                WindCase.CASE_3_2B_23,
            ),
            (
                # Case 3_2B_25
                # Input Fingerprint: 333333333333333322223333
                # - WF0 != WF1 not juxtaposed
                # - no WD0, WD10 and WD12
                generate_valid_times(periods=24),
                [34.9] * 10 + [15.0] * 4 + [45.0] * 10,
                [np.nan] * 14 + [0.1] * 5 + [136.0] * 5,
                WindCase.CASE_3_2B_25,
            ),
            (
                # Case 3_2B_27
                # Input Fingerprint: 333333333333333322223333
                # - WF0 != WF1 not juxtaposed
                # - WD0, WD1, WD10 and WD12
                generate_valid_times(periods=24),
                [34.9] * 10 + [15.0] * 4 + [45.0] * 10,
                [0.1] * 5 + [136.0] * 5 + [np.nan] * 4 + [22.5] * 5 + [158.0] * 5,
                WindCase.CASE_3_2B_27,
            ),
            (
                # Case 3_2B_29
                # Input Fingerprint: 333333333333333322223333
                # - WF0 != WF1 not juxtaposed
                # - no WD0
                generate_valid_times(periods=24),
                [34.9] * 16 + [15.0] * 4 + [45.0] * 4,
                [np.nan] * 24,
                WindCase.CASE_3_2B_29,
            ),
            (
                # Case 3_2B_31
                # Input Fingerprint: 333333322222222333333333
                # - WF00 = 30 km/h, WF01 = 50 km/h, WF1 = 40 km/h
                # - Wd0, no WD1
                generate_valid_times(periods=24),
                [34.9] * 3 + [45.0] * 4 + [15.0] * 8 + [35.0] * 9,
                [0.1] * 24,
                WindCase.CASE_3_2B_31,
            ),
            (
                # Case 3_2B_32
                # Input Fingerprint: 333333322222222333333333
                # - WF00 = 30 km/h, WF01 = 50 km/h, WF1 = 40 km/h
                # - WD0, WD1
                generate_valid_times(periods=24),
                [34.9] * 3 + [45.0] * 4 + [15.0] * 8 + [35.0] * 9,
                [0.1] * 7 + [np.nan] * 8 + [90.0] * 9,
                WindCase.CASE_3_2B_32,
            ),
            (
                # Case 3_2B_33
                # Input Fingerprint: 333333322222222333333333
                # - WF00 = 30 km/h, WF01 = 50 km/h, WF1 = 40 km/h
                # - WD0, no WD1
                generate_valid_times(periods=24),
                [34.9] * 3 + [45.0] * 4 + [15.0] * 8 + [35.0] * 9,
                [0.1] * 7 + [np.nan] * 17,
                WindCase.CASE_3_2B_33,
            ),
            (
                # Case 3_2B_34
                # Input Fingerprint: 333333322222222333333333
                # - WF00 = 30 km/h, WF01 = 50 km/h, WF1 = 40 km/h
                # - no WD0, WD1
                generate_valid_times(periods=24),
                [34.9] * 3 + [45.0] * 4 + [15.0] * 8 + [35.0] * 9,
                [np.nan] * 15 + [0.1] * 9,
                WindCase.CASE_3_2B_34,
            ),
            (
                # Case 3_2B_35
                # Input Fingerprint: 333333333333333322223333
                # - WF00 = 30 km/h, WF01 = 50 km/h, WF1 = 40 km/h
                # - WD00, WD01 and WD1
                generate_valid_times(periods=24),
                [34.9] * 3 + [45.0] * 4 + [15.0] * 8 + [35.0] * 9,
                [0.1] * 4 + [136.0] * 3 + [np.nan] * 8 + [271.0] * 9,
                WindCase.CASE_3_2B_35,
            ),
            (
                # Case 3_2B_36
                # Input Fingerprint: 333333322222222333333333
                # - WF00 = 30 km/h, WF01 = 50 km/h, WF1 = 40 km/h
                # - WD00, WD01 and no WD1
                generate_valid_times(periods=24),
                [34.9] * 3 + [45.0] * 4 + [15.0] * 8 + [35.0] * 9,
                [0.1] * 4 + [136.0] * 3 + [np.nan] * 17,
                WindCase.CASE_3_2B_36,
            ),
            (
                # Case 3_2B_37
                # Input Fingerprint: 333333322222222333333333
                # - WF00 = 30 km/h, WF01 = 50 km/h, WF1 = 40 km/h
                # - WD0, WD10, WD11
                generate_valid_times(periods=24),
                [34.9] * 3 + [45.0] * 4 + [15.0] * 8 + [35.0] * 9,
                [0.1] * 7 + [np.nan] * 8 + [135.0] * 4 + [271.0] * 5,
                WindCase.CASE_3_2B_37,
            ),
            (
                # Case 3_2B_38
                # Input Fingerprint: 333333322222222333333333
                # - WF00 = 30 km/h, WF01 = 50 km/h, WF1 = 40 km/h
                # - WD00, WD01 and no WD1
                generate_valid_times(periods=24),
                [34.9] * 3 + [45.0] * 4 + [15.0] * 8 + [35.0] * 9,
                [np.nan] * 7 + [np.nan] * 8 + [0.1] * 4 + [136.0] * 5,
                WindCase.CASE_3_2B_38,
            ),
            (
                # Case 3_2B_39
                # Input Fingerprint: 333333333333333322223333
                # - WF0 != WF1 not juxtaposed
                # - WD0, WD1, WD10 and WD12
                generate_valid_times(periods=24),
                [34.9] * 3 + [45.0] * 4 + [15.0] * 8 + [35.0] * 9,
                [0.1] * 3 + [136.0] * 4 + [np.nan] * 8 + [22.5] * 5 + [158.0] * 4,
                WindCase.CASE_3_2B_39,
            ),
            (
                # Case 3_2B_40
                # Input Fingerprint: 333333322222222333333333
                # - WF00 = 30 km/h, WF01 = 50 km/h, WF1 = 40 km/h
                # - no WD
                generate_valid_times(periods=24),
                [34.9] * 3 + [45.0] * 4 + [15.0] * 8 + [35.0] * 9,
                [np.nan] * 24,
                WindCase.CASE_3_2B_40,
            ),
        ],
    )
    @patch(
        "mfire.text.wind.reducers.wind_summary_builder.WindSummaryBuilder."
        "THRESHOLD_MINUS_NUM",
        11,
    )  # To have WindSummaryBuilder.THRESHOLD_MINUS_NUM = 11."""
    def test_two_type3_blocks_threshold_minus_num_11(
        self,
        valid_times,
        data_wf,
        data_wd,
        case_exp: WindCase,
        assert_equals_result,
    ):
        """Test when there are 2 type 3 WindBlocks with THRESHOLD_MINUS_NUM = 11."""
        self._check(
            valid_times,
            None,
            data_wf,
            data_wd,
            case_exp,
            assert_equals_result,
        )


class TestDirectors:
    """TestDirectors class."""

    COMPOSITE_FACTORY: CompositeFactory1x1 = CompositeFactory1x1

    def _check(
        self,
        valid_times,
        data_gust,
        data_wf,
        data_wd,
        assert_equals_result,
    ):
        """Check directors resulting text with both wind and gust input data."""

        # Create composite
        composite = self.COMPOSITE_FACTORY.get_composite_when_term_data_is_one_number(
            valid_times=valid_times,
            data_wind=data_wf,
            data_dir=data_wd,
            data_gust=data_gust,
        )

        # Create director
        director: WindDirector = WindDirector()

        # Run director
        assert_equals_result(director.compute(geo_id="", composite=composite))

    @pytest.mark.parametrize(
        "valid_times, data_gust, data_wf, data_wd",
        [
            (
                # No wind, no gust
                generate_valid_times(periods=12),
                [0.0] * 12,
                [0.0] * 12,
                [np.nan] * 12,
            ),
            (
                # Wind with type 1 and gust
                generate_valid_times(periods=12),
                [60.0] * 12,
                [14.0] * 12,
                [np.nan] * 12,
            ),
            (
                # Wind with type 2 and gust
                generate_valid_times(periods=12),
                [60.0] * 12,
                [16.0] * 12,
                [np.nan] * 12,
            ),
            (
                # Wind with type 1 and 2 and gust
                generate_valid_times(periods=12),
                [60.0] * 12,
                [5.0] * 6 + [16.0] * 6,
                [np.nan] * 12,
            ),
            (
                # Wind with type 3 and gust
                generate_valid_times(periods=12),
                [60.0] * 12,
                [5.0] * 6 + [90.0] * 6,
                [np.nan] * 12,
            ),
        ],
    )
    def test(self, valid_times, data_gust, data_wf, data_wd, assert_equals_result):
        """Test function which call _check method."""
        self._check(
            valid_times,
            data_gust,
            data_wf,
            data_wd,
            assert_equals_result,
        )


class TestWindDirectorExtra:
    """TestWindDirectorExtra class."""

    class WindDirectorWithExtra(WindDirector):
        WITH_EXTRA: bool = True

    class WindDirectorWithoutExtra(WindDirector):
        WITH_EXTRA: bool = False

    @pytest.mark.parametrize(
        "valid_times, data_gust, data_wf, data_wd",
        [
            (
                # Gust and type 2 wind
                generate_valid_times(periods=3),
                [60.0] * 3,
                [16.0] * 3,
                [np.nan] * 3,
            )
        ],
    )
    def test(self, valid_times, data_gust, data_wf, data_wd):
        """Test extra content produced by a director."""
        # Create composite
        composite = CompositeFactory1x1.get_composite_when_term_data_is_one_number(
            valid_times=valid_times,
            data_wind=data_wf,
            data_dir=data_wd,
            data_gust=data_gust,
        )

        director = self.WindDirectorWithExtra()
        _, extra_content_text = director._compute_synthesis_elements(
            geo_id="", composite=composite
        )
        assert extra_content_text is not None

        director = self.WindDirectorWithoutExtra()
        _, extra_content_text = director._compute_synthesis_elements(
            geo_id="", composite=composite
        )
        assert extra_content_text is None

from datetime import datetime

import numpy as np
import pytest

import mfire.utils.mfxarray as xr
from mfire.text.wind.exceptions import WindSynthesisError
from mfire.text.wind.base import BaseParamBuilder
from mfire.text.wind.const import ERROR_CASE
from mfire.text.wind.reducers.wind_summary_builder import WindSummaryBuilder
from mfire.text.wind.reducers.wind_summary_builder.case3 import Case3SummaryBuilder
from mfire.text.wind.reducers.wind_summary_builder.case3.wind_block import WindBlock
from mfire.text.wind.reducers.wind_summary_builder.helpers import (
    MetaData,
    WindCase,
    WindType,
)
from mfire.text.wind.reducers.wind_summary_builder.wind_direction import (
    WindDirection,
    WindDirectionPeriod,
)
from mfire.text.wind.reducers.wind_summary_builder.wind_force import (
    WindForce,
    WindForcePeriod,
)
from mfire.utils.date import Datetime

from tests.text.utils import generate_valid_times, generate_valid_times_v2

from .factories import (
    CompositeFactory1x1,
    CompositeFactory2x2,
    CompositeFactory2x2Type1,
    CompositeFactory5x2,
    CompositeFactory6x2,
    CompositeFactory6x4,
)
from .utils import data_to_ndarray


class TestWindDataConversion:
    @pytest.mark.parametrize(
        "valid_times, data, units_compo, units_data, data_exp, unit_exp",
        [
            # All parametrizations produce examples with only type 1 terms: then the
            # data is not filtered
            (
                generate_valid_times(periods=2),
                [[[0.0, 1.0], [np.nan, 10.0]], [[4.0, np.nan], [11.0, 14.0]]],
                {"wind": "km/h"},
                {"wind": "km/h"},
                [[[0.0, 1.0], [0.0, 10.0]], [[4.0, 0.0], [11.0, 14.0]]],
                "km/h",
            ),
            (
                generate_valid_times(periods=2),
                [[[0.0, 1.0], [0.0, 10.0]], [[4.0, 0.0], [11.0, 14.0]]],
                {"wind": "km/h"},
                {"wind": "km/h"},
                [[[0.0, 1.0], [0.0, 10.0]], [[4.0, 0.0], [11.0, 14.0]]],
                "km/h",
            ),
            (
                generate_valid_times(periods=2),
                [[[0.0, 1.0], [np.nan, 1.0]], [[1.0, np.nan], [1.0, 1.0]]],
                {"wind": "km/h"},
                {"wind": "m s**-1"},
                3.6 * np.array([[[0.0, 1.0], [0.0, 1.0]], [[1.0, 0.0], [1.0, 1.0]]]),
                "km/h",
            ),
            (
                generate_valid_times(periods=2),
                [[[0.0, 1.0], [0.0, 1.0]], [[1.0, 0.0], [1.0, 1.0]]],
                {"wind": "km/h"},
                {"wind": "m s**-1"},
                3.6 * np.array([[[0.0, 1.0], [0.0, 1.0]], [[1.0, 0.0], [1.0, 1.0]]]),
                "km/h",
            ),
        ],
    )
    def test_wind_units_conversion(
        self, valid_times, data, units_compo, units_data, data_exp, unit_exp
    ):
        """Test wind force initialization and conversion.

        Nan values are replaced by 0 and the wind force unit has to be km/h.
        """
        composite = CompositeFactory2x2().get(
            valid_times=valid_times,
            data_wind=data,
            units_compo=units_compo,
            units_data=units_data,
        )
        dataset = composite.compute()
        summary_builder = WindSummaryBuilder(composite, dataset)

        # Check unit
        data_array: xr.DataArray = summary_builder.data_wf
        assert data_array.units == unit_exp

        # Check value after conversion
        np.testing.assert_allclose(data_array.values, data_exp)

    @pytest.mark.parametrize(
        "valid_times, data, units_compo, units_data, data_exp, unit_exp",
        [
            (
                generate_valid_times(periods=2),
                [[[0.1, 1.0], [np.nan, 20.0]], [[4.0, np.nan], [15.0, 18.0]]],
                {"direction": "deg"},
                {"direction": "deg"},
                [[[0.1, 1.0], [np.nan, 20.0]], [[4.0, np.nan], [15.0, 18.0]]],
                "deg",
            ),
            (
                generate_valid_times(periods=2),
                [[[0.1, 1.0], [np.nan, 20.0]], [[4.0, np.nan], [15.0, 18.0]]],
                {"direction": "deg"},
                {"direction": "°"},
                [[[0.1, 1.0], [np.nan, 20.0]], [[4.0, np.nan], [15.0, 18.0]]],
                "deg",
            ),
        ],
    )
    def test_direction_units_conversion(
        self, valid_times, data, units_compo, units_data, data_exp, unit_exp
    ):
        """Test wind direction initialization and conversion.

        The wind direction unit has to be km/h.
        """
        composite = CompositeFactory2x2Type1().get(
            valid_times=valid_times,
            data_dir=data,
            units_compo=units_compo,
            units_data=units_data,
        )
        dataset = composite.compute()
        summary_builder = WindSummaryBuilder(composite, dataset)

        # Check unit
        data_array: xr.DataArray = summary_builder.data_wd
        assert data_array.units == unit_exp

        # Check value after conversion
        np.testing.assert_allclose(data_array.values, data_exp)


class TestWindSummaryInitialization:
    def test_data_points_counter(self):
        valid_times = generate_valid_times(periods=1)

        composite = CompositeFactory5x2().get(
            valid_times=valid_times, data_wind=np.full((5, 2), 30.0)
        )
        dataset = composite.compute()
        summary_builder = WindSummaryBuilder(composite, dataset)

        data_points_counter_exp = 5 * 2
        assert summary_builder.metadata.data_points_counter == data_points_counter_exp

    @pytest.mark.parametrize(
        "term_data, lower_bound, count_exp, percent_exp",
        [
            (
                [
                    [1.0, 2.0],
                    [3.0, 3.0],
                    [4.0, 5.0],
                    [30.0, 31.0],
                    [32.0, 33.0],
                ],
                30.0,
                4,
                40.0,
            ),
            (
                [
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [30.0, 31.0],
                    [32.0, 33.0],
                    [34.0, 35.0],
                ],
                30.0,
                6,
                60.0,
            ),
            (
                [
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, 33.0],
                    [34.0, 35.0],
                ],
                30.0,
                3,
                30.0,
            ),
            (np.full((5, 2), np.nan), 30.0, 0, 0.0),
            (np.full((5, 2), 0.0), 30.0, 0, 0.0),
        ],
    )
    def test_count_points(self, term_data, lower_bound, count_exp, percent_exp):
        valid_times = generate_valid_times(periods=1)
        valid_time = valid_times[0]

        composite = CompositeFactory5x2().get(
            valid_times=valid_times, data_wind=term_data
        )
        dataset = composite.compute()
        summary_builder = WindSummaryBuilder(composite, dataset)

        data = summary_builder.data_wf.sel(valid_time=valid_time)
        count, percent = summary_builder.count_points(data, data >= lower_bound)

        assert count == count_exp
        assert percent == percent_exp

    @staticmethod
    def _check_wind_summary_builder_wind_types(
        summary_builder: WindSummaryBuilder, expected_wind_types: list[WindType]
    ):
        expected = tuple([wt for wt in expected_wind_types])
        assert summary_builder.wind_types == expected
        assert summary_builder.wind_types_set == set(expected)

    def _check_wind_summary_builder(
        self,
        composite_factory,
        valid_times,
        data_wf,
        data_wd,
        wind_types_exp: list[WindType],
        case_exp: WindCase,
        metadata_exp: MetaData,
        exp_data_wd,
    ):
        """Test WindSummaryBuilder.

        Test the most sensitive data from the initialization to the summary dictionary
        generation:
        - term types
        - case
        - metadata
        - pd_summary
        - data_wd
        """
        # Compute the composite
        composite = composite_factory.get(
            valid_times=valid_times, data_wind=data_wf, data_dir=data_wd
        )
        dataset = composite.compute()
        summary_builder = WindSummaryBuilder(composite, dataset)

        # Test terms types
        self._check_wind_summary_builder_wind_types(summary_builder, wind_types_exp)

        # Test case nbr
        assert summary_builder.case_family == case_exp

        # Generate summary
        reference_datetime: Datetime = Datetime(datetime.now())
        summary_builder.compute(reference_datetime)

        # Test metadata
        assert summary_builder.metadata == metadata_exp
        assert summary_builder.threshold == metadata_exp.threshold

        # Check data_wf and data_wd values
        exp_data_wd = data_to_ndarray(exp_data_wd)
        np.testing.assert_allclose(summary_builder.data_wd.values, exp_data_wd)

        # Test terms types
        self._check_wind_summary_builder_wind_types(summary_builder, wind_types_exp)

    @pytest.mark.parametrize(
        "valid_times, data_wf, data_wd, wind_types_exp, case_exp, metadata_exp, "
        "exp_data_wd",
        [
            # All point have no wind force --> each point has a wind force < 15
            # 0/10 points (10. %) with a wind force >= 30 --> not a type 3
            # 0/10 points (10. %) with a wind force >= 15 --> not a type 2
            # --> this is a term of type 1
            # So data_wf and data_wd are not filtered.
            (
                generate_valid_times(periods=1),  # valid_times
                np.full((5, 2), np.nan),  # data_wf
                np.full((5, 2), np.nan),  # data_wd
                [WindType.TYPE_1],  # wind_types_exp
                WindCase.CASE_1,  # case nbr
                MetaData(
                    data_points_counter=10,
                    threshold_accumulated=0.0,
                    threshold_hours_max=0.0,
                    threshold=0.0,
                    filtering_threshold_t2=0.0,
                    filtering_threshold_t3=0.0,
                    t2_percent_max_detection=0.0,
                    t3_percent_max_detection=0.0,
                    t3_percent_max_confirmation=0.0,
                ),
                np.full((5, 2), np.nan),  # exp_data_wd
            ),
            # Each point has a wind force < 15
            # 0/10 points (10. %) with a wind force >= 30 --> not a type 3
            # 0/10 points (10. %) with a wind force >= 15 --> not a type 2
            # --> this is a term of type 1
            # So data_wf and data_wd are not filtered.
            (
                generate_valid_times(periods=1),
                [
                    [1.0, 2.0],
                    [4.0, 5.0],
                    [6.0, 7.0],
                    [np.nan, np.nan],
                    [8.0, 14.9],
                ],
                [
                    [10.0, 11.0],
                    [12.0, 13.0],
                    [14.0, 15.0],
                    [np.nan, np.nan],
                    [18.0, 19.0],
                ],
                [WindType.TYPE_1],
                WindCase.CASE_1,
                MetaData(
                    data_points_counter=10,
                    threshold_accumulated=1.8,
                    threshold_hours_max=1.8,
                    threshold=1.8,
                    filtering_threshold_t2=0.0,
                    filtering_threshold_t3=0.0,
                    t2_percent_max_detection=0.0,
                    t3_percent_max_detection=0.0,
                    t3_percent_max_confirmation=0.0,
                ),
                [
                    [10.0, 11.0],
                    [12.0, 13.0],
                    [14.0, 15.0],
                    [np.nan, np.nan],
                    [18.0, 19.0],
                ],
            ),
            # A point has a wind force in [15, 30]
            # 0/10 points (10. %) with a wind force >= 30 --> not a type 3
            # 1/10 points (10. %) with a wind force >= 15 --> type 2
            # So data_wf and data_wd are filtered.
            (
                generate_valid_times(periods=1),
                [
                    [1.0, 2.0],
                    [4.0, 5.0],
                    [6.0, 7.0],
                    [np.nan, np.nan],
                    [8.0, 15.0],
                ],
                [
                    [10.0, 11.0],
                    [12.0, 13.0],
                    [14.0, 15.0],
                    [np.nan, np.nan],
                    [18.0, 19.0],
                ],
                [WindType.TYPE_2],
                WindCase.CASE_2,
                MetaData(
                    data_points_counter=10,
                    threshold_accumulated=1.8,
                    threshold_hours_max=1.8,
                    threshold=1.8,
                    filtering_threshold_t2=15.0,
                    filtering_threshold_t3=0.0,
                    t2_percent_max_detection=10.0,
                    t3_percent_max_detection=0.0,
                    t3_percent_max_confirmation=0.0,
                ),
                [
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, 19.0],
                ],
            ),
            # Threshold = 6.5
            # 1/10 points (10. %) with a wind force >= 30 --> possibly a type 3
            # 1/10 points (10. %) with a wind force >= threshold --> type 3
            (
                generate_valid_times(periods=1),
                [
                    [1.0, 2.0],
                    [4.0, 5.0],
                    [6.0, 7.0],
                    [np.nan, np.nan],
                    [8.0, 30.0],
                ],
                [
                    [10.0, 11.0],
                    [12.0, 13.0],
                    [14.0, 15.0],
                    [np.nan, np.nan],
                    [18.0, 19.0],
                ],
                [WindType.TYPE_3],
                WindCase.CASE_3,
                MetaData(
                    data_points_counter=10,
                    threshold_accumulated=10.1,
                    threshold_hours_max=10.1,
                    threshold=10.1,
                    filtering_threshold_t2=15.0,
                    filtering_threshold_t3=10.1,
                    t2_percent_max_detection=0.0,
                    t3_percent_max_detection=10.0,
                    t3_percent_max_confirmation=10.0,
                ),
                [
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, 19.0],
                ],
            ),
        ],
    )
    def test_wind_summary_builder_5x2(
        self,
        valid_times,
        data_wf,
        data_wd,
        wind_types_exp: list[WindType],
        case_exp: WindCase,
        metadata_exp: MetaData,
        exp_data_wd,
    ):
        """Test the WindSummaryBuilder with terms of 5x2 size."""
        self._check_wind_summary_builder(
            CompositeFactory5x2,
            valid_times,
            data_wf,
            data_wd,
            wind_types_exp,
            case_exp,
            metadata_exp,
            exp_data_wd,
        )

    @pytest.mark.parametrize(
        "valid_times, data_wf, data_wd, wind_types_exp, case_exp, metadata_exp, "
        "exp_data_wd",
        [
            # Threshold = 4.0
            # 1/12 points (8.3 %) with a wind force >= 30 --> possibly a type 3
            # 1/12 points (8.3 %) with a wind force >= threshold --> type 2
            (
                generate_valid_times(periods=1),
                [
                    [1.0, 1.0],
                    [np.nan, 1.0],
                    [1.0, 1.0],
                    [1.0, 1.0],
                    [1.0, 1.0],
                    [1.0, 30.0],
                ],
                [
                    [10.0, 11.0],
                    [np.nan, 13.0],
                    [14.0, 15.0],
                    [16.0, 17.0],
                    [18.0, 19.0],
                    [20.0, 21.0],
                ],
                [WindType.TYPE_2],
                WindCase.CASE_2,
                MetaData(
                    data_points_counter=12,
                    threshold_accumulated=4.0,
                    threshold_hours_max=4.0,
                    threshold=4.0,
                    filtering_threshold_t2=15.0,
                    filtering_threshold_t3=0.0,
                    t2_percent_max_detection=0.0,
                    t3_percent_max_detection=8.3,
                    t3_percent_max_confirmation=8.3,
                ),
                [
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, 21.0],
                ],
            ),
            # Threshold = 8.4
            # 1/12 points (8.3 %) with a wind force >= 30 --> possibly a type 3
            # 2/12 points (16.7 %) with a wind force >= threshold --> type 3
            (
                generate_valid_times(periods=1),
                [
                    [1.0, 2.0],
                    [np.nan, 3.0],
                    [np.nan, 5.0],
                    [6.0, 7.0],
                    [8.0, 9.0],
                    [8.0, 30.0],
                ],
                [
                    [10.0, 11.0],
                    [np.nan, 13.0],
                    [np.nan, 15.0],
                    [16.0, 17.0],
                    [18.0, 19.0],
                    [20.0, 21.0],
                ],
                [WindType.TYPE_3],
                WindCase.CASE_3,
                MetaData(
                    data_points_counter=12,
                    threshold_accumulated=8.4,
                    threshold_hours_max=8.4,
                    threshold=8.4,
                    filtering_threshold_t2=15.0,
                    filtering_threshold_t3=8.4,
                    t2_percent_max_detection=0.0,
                    t3_percent_max_detection=8.3,
                    t3_percent_max_confirmation=16.7,
                ),
                [
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, np.nan],
                    [np.nan, 19.0],
                    [np.nan, 21.0],
                ],
            ),
            # Threshold = 11.8
            # - term 0: all points < 15 --> type 1
            # - term 1: 4/12 (33.3 %) points with wind >= 15 --> type 2
            # - term 2: 2/12 (16.7 %) points with wind force >= 30 --> possibly a type 3
            # 4/12 points (33.3 %) with a wind force >= threshold --> type 3
            (
                generate_valid_times(periods=3),
                [
                    [
                        [1.0, 2.0],
                        [3.0, 3.0],
                        [4.0, 5.0],
                        [6.0, 7.0],
                        [8.0, 9.0],
                        [10.0, 11.0],
                    ],
                    [
                        [1.0, 2.0],
                        [3.0, 3.0],
                        [4.0, 5.0],
                        [6.0, 7.0],
                        [16.0, 17.0],
                        [18.0, 19.0],
                    ],
                    [
                        [1.0, 2.0],
                        [3.0, 3.0],
                        [4.0, 5.0],
                        [6.0, 7.0],
                        [16.0, 17.0],
                        [30.0, 30.0],
                    ],
                ],
                [
                    [
                        [1.0, 2.0],
                        [3.0, 3.0],
                        [4.0, 5.0],
                        [6.0, 7.0],
                        [16.0, 17.0],
                        [18.0, 19.0],
                    ],
                    [
                        [10.0, 11.0],
                        [12.0, 13.0],
                        [14.0, 15.0],
                        [16.0, 17.0],
                        [18.0, 19.0],
                        [20.0, 21.0],
                    ],
                    [
                        [22.0, 23.0],
                        [24.0, 25.0],
                        [26.0, 27.0],
                        [28.0, 29.0],
                        [30.0, 31.0],
                        [32.0, 33.0],
                    ],
                ],
                [WindType.TYPE_1, WindType.TYPE_2, WindType.TYPE_3],
                WindCase.CASE_3,
                MetaData(
                    data_points_counter=12,
                    threshold_accumulated=11.8,
                    threshold_hours_max=20.0,
                    threshold=11.8,
                    filtering_threshold_t2=15.0,
                    filtering_threshold_t3=11.8,
                    t2_percent_max_detection=33.3,
                    t3_percent_max_detection=16.7,
                    t3_percent_max_confirmation=33.3,
                ),
                [
                    [
                        [np.nan, np.nan],
                        [np.nan, np.nan],
                        [np.nan, np.nan],
                        [np.nan, np.nan],
                        [18.0, 19.0],
                        [20.0, 21.0],
                    ],
                    [
                        [np.nan, np.nan],
                        [np.nan, np.nan],
                        [np.nan, np.nan],
                        [np.nan, np.nan],
                        [30.0, 31.0],
                        [32.0, 33.0],
                    ],
                ],
            ),
            # Threshold = 8.4
            # - term 0: all points < 15 --> type 1
            # - term 1: 4/12 (33.3 %) points with wind >= 15 --> type 2
            # - term 2: 1/12 (8.3 %) points with wind force >= 30 --> possibly a type 3
            # 1/12 points (8.3 %) with a wind force >= threshold --> type 2
            (
                generate_valid_times(periods=3),
                [
                    [
                        [1.0, 2.0],
                        [3.0, 3.0],
                        [4.0, 5.0],
                        [6.0, 7.0],
                        [8.0, 9.0],
                        [10.0, 11.0],
                    ],
                    [
                        [1.0, 2.0],
                        [3.0, 3.0],
                        [4.0, 5.0],
                        [6.0, 7.0],
                        [16.0, 17.0],
                        [18.0, 19.0],
                    ],
                    [
                        [1.0, 1.0],
                        [1.0, 1.0],
                        [1.0, 1.0],
                        [1.0, 1.0],
                        [1.0, 5.0],
                        [np.nan, 30.0],
                    ],
                ],
                [
                    [
                        [1.0, 2.0],
                        [3.0, 3.0],
                        [4.0, 5.0],
                        [6.0, 7.0],
                        [16.0, 17.0],
                        [18.0, 19.0],
                    ],
                    [
                        [10.0, 11.0],
                        [12.0, 13.0],
                        [14.0, 15.0],
                        [16.0, 17.0],
                        [18.0, 19.0],
                        [20.0, 21.0],
                    ],
                    [
                        [22.0, 23.0],
                        [24.0, 25.0],
                        [26.0, 27.0],
                        [28.0, 29.0],
                        [30.0, 31.0],
                        [32.0, 33.0],
                    ],
                ],
                [WindType.TYPE_1, WindType.TYPE_2, WindType.TYPE_2],
                WindCase.CASE_2,
                MetaData(
                    data_points_counter=12,
                    threshold_accumulated=8.2,
                    threshold_hours_max=8.4,
                    threshold=8.2,
                    filtering_threshold_t2=15,
                    filtering_threshold_t3=0.0,
                    t2_percent_max_detection=33.3,
                    t3_percent_max_detection=8.3,
                    t3_percent_max_confirmation=8.3,
                ),
                [
                    [
                        [np.nan, np.nan],
                        [np.nan, np.nan],
                        [np.nan, np.nan],
                        [np.nan, np.nan],
                        [18.0, 19.0],
                        [20.0, 21.0],
                    ],
                    [
                        [np.nan, np.nan],
                        [np.nan, np.nan],
                        [np.nan, np.nan],
                        [np.nan, np.nan],
                        [np.nan, np.nan],
                        [np.nan, 33.0],
                    ],
                ],
            ),
        ],
    )
    def test_wind_summary_builder_6x2(
        self,
        valid_times,
        data_wf,
        data_wd,
        wind_types_exp: list[WindType],
        case_exp: WindCase,
        metadata_exp: MetaData,
        exp_data_wd,
    ):
        """Test the WindSummaryBuilder with terms of 5x2 size."""
        self._check_wind_summary_builder(
            CompositeFactory6x2,
            valid_times,
            data_wf,
            data_wd,
            wind_types_exp,
            case_exp,
            metadata_exp,
            exp_data_wd,
        )

    @pytest.mark.parametrize(
        "valid_times, data_wf, data_wd, wind_types_exp, case_exp, metadata_exp, "
        "exp_data_wd",
        [
            # Threshold = 4.0
            # There is point >= 15 --> --> possibly a type 2
            # 1/24 points (4.1 %) with a wind force >= 15 --> type 1
            (
                generate_valid_times(periods=1),
                [
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 20.0],
                ],
                [
                    [1.0, 2.0, 3.0, 3.0],
                    [5.0, 6.0, 7.0, 8.0],
                    [9.0, 10.0, 11.0, 12.0],
                    [13.0, 14.0, 15.0, 16.0],
                    [17.0, 18.0, 19.0, 20.0],
                    [21.0, 22.0, 23.0, 24.0],
                ],
                [WindType.TYPE_1],
                WindCase.CASE_1,
                MetaData(
                    data_points_counter=24,
                    threshold_accumulated=0.0,
                    threshold_hours_max=0.0,
                    threshold=0.0,
                    filtering_threshold_t2=0.0,
                    filtering_threshold_t3=0.0,
                    t2_percent_max_detection=4.2,
                    t3_percent_max_detection=0.0,
                    t3_percent_max_confirmation=0.0,
                ),
                [
                    [1.0, 2.0, 3.0, 3.0],
                    [5.0, 6.0, 7.0, 8.0],
                    [9.0, 10.0, 11.0, 12.0],
                    [13.0, 14.0, 15.0, 16.0],
                    [17.0, 18.0, 19.0, 20.0],
                    [21.0, 22.0, 23.0, 24.0],
                ],
            ),
            # Threshold = 4.0
            # There is point >= 30 --> --> possibly a type 3
            # - 1/24 points (4.1 %) with a wind force >= 30 --> not a type 3
            # - 1/24 points (4.1 %) with a wind force >= 15 --> not a type 2
            # so this is a term of type 1
            (
                generate_valid_times(periods=1),
                [
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 30.0],
                ],
                [
                    [1.0, 2.0, 3.0, 3.0],
                    [5.0, 6.0, 7.0, 8.0],
                    [9.0, 10.0, 11.0, 12.0],
                    [13.0, 14.0, 15.0, 16.0],
                    [17.0, 18.0, 19.0, 20.0],
                    [21.0, 22.0, 23.0, 24.0],
                ],
                [WindType.TYPE_1],
                WindCase.CASE_1,
                MetaData(
                    data_points_counter=24,
                    threshold_accumulated=0.0,
                    threshold_hours_max=0.0,
                    threshold=0.0,
                    filtering_threshold_t2=0.0,
                    filtering_threshold_t3=0.0,
                    t2_percent_max_detection=4.2,
                    t3_percent_max_detection=4.2,
                    t3_percent_max_confirmation=0.0,
                ),
                [
                    [1.0, 2.0, 3.0, 3.0],
                    [5.0, 6.0, 7.0, 8.0],
                    [9.0, 10.0, 11.0, 12.0],
                    [13.0, 14.0, 15.0, 16.0],
                    [17.0, 18.0, 19.0, 20.0],
                    [21.0, 22.0, 23.0, 24.0],
                ],
            ),
            # Threshold = 4.0
            # There is point >= 30 --> --> possibly a type 3
            # - 1/24 points (4.1 %) with a wind force >= 30 --> not a type 3
            # - 2/24 points (8.3 %) with a wind force >= 15 --> type 2
            # so this is a term of type 1
            (
                generate_valid_times(periods=1),
                [
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 20.0, 30.0],
                ],
                [
                    [1.0, 2.0, 3.0, 3.0],
                    [5.0, 6.0, 7.0, 8.0],
                    [9.0, 10.0, 11.0, 12.0],
                    [13.0, 14.0, 15.0, 16.0],
                    [17.0, 18.0, 19.0, 20.0],
                    [21.0, 22.0, 23.0, 24.0],
                ],
                [WindType.TYPE_2],
                WindCase.CASE_2,
                MetaData(
                    data_points_counter=24,
                    threshold_accumulated=7.1,
                    threshold_hours_max=7.1,
                    threshold=7.1,
                    filtering_threshold_t2=15.0,
                    filtering_threshold_t3=0.0,
                    t2_percent_max_detection=8.3,
                    t3_percent_max_detection=4.2,
                    t3_percent_max_confirmation=0.0,
                ),
                [
                    [np.nan, np.nan, np.nan, np.nan],
                    [np.nan, np.nan, np.nan, np.nan],
                    [np.nan, np.nan, np.nan, np.nan],
                    [np.nan, np.nan, np.nan, np.nan],
                    [np.nan, np.nan, np.nan, np.nan],
                    [np.nan, np.nan, 23.0, 24.0],
                ],
            ),
        ],
    )
    def test_wind_summary_builder_6x4(
        self,
        valid_times,
        data_wf,
        data_wd,
        wind_types_exp: list[WindType],
        case_exp: WindCase,
        metadata_exp: MetaData,
        exp_data_wd,
    ):
        """Test the WindSummaryBuilder with terms of 5x2 size."""
        self._check_wind_summary_builder(
            CompositeFactory6x4,
            valid_times,
            data_wf,
            data_wd,
            wind_types_exp,
            case_exp,
            metadata_exp,
            exp_data_wd,
        )


class TestGenerateSummary:
    @staticmethod
    def _compare_summary(summary: dict, summary_exp: dict):
        summary[WindSummaryBuilder.WIND_FORCE].pop(BaseParamBuilder.EXTRA_KEY, None)

        assert summary == summary_exp


class TestGenerateSummaryCase1(TestGenerateSummary):
    class CompositeFactory(CompositeFactory2x2):
        LON = [30, 31]
        LAT = [40, 41]

    def test(self):
        valid_times = generate_valid_times(periods=1)

        composite = self.CompositeFactory().get(
            valid_times=valid_times, data_wind=np.full((2, 2), 10.0)
        )
        dataset = composite.compute()
        summary_builder = WindSummaryBuilder(composite, dataset)
        reference_datetime: Datetime = Datetime(datetime.now())
        summary = summary_builder.compute(reference_datetime)

        summary_exp = {"wind": {"case": "wind_case_1"}}
        self._compare_summary(summary, summary_exp)


class TestGenerateSummaryCase3:
    @staticmethod
    def create_master_summary_builder_from_composite(composite):
        dataset = composite.compute()
        summary_builder = WindSummaryBuilder(composite, dataset)
        return summary_builder

    def check_block_builder(self, composite, blocks_exp, case_exp):
        reference_datetime: Datetime = Datetime(datetime.now())

        # Create master summary builder, specially to filter the data
        summary_builder = self.create_master_summary_builder_from_composite(composite)

        case3_summary_builder: Case3SummaryBuilder = Case3SummaryBuilder(
            summary_builder.pd_summary, summary_builder.data_wd, summary_builder.data_wf
        )
        sub_summary = case3_summary_builder.run(reference_datetime)

        # Check Fingerprints
        assert case3_summary_builder.blocks_builder.blocks == blocks_exp

        # Check case nbr
        assert sub_summary["case"] == case_exp.value

    @pytest.mark.parametrize(
        "valid_times, data_wf, data_wd, blocks_exp, case_exp",
        [
            (
                # Input Fingerprint: 111222222233333333333333
                # Max wind force is in the last type 3 group.
                # 2 WindForcePeriod, 1 WindDirectionPeriod
                generate_valid_times(periods=24),
                [10.0] * 3 + [15.0] * 7 + [30.0] * 10 + [40.0] * 4,
                [90.0] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 2, 2, 0, 0),
                        Datetime(2023, 1, 2, 9, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 2, 0, 0),
                                Datetime(2023, 1, 2, 9, 0, 0),
                                WindDirection([90.0, 90.0]),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 9, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 9, 0, 0),
                                Datetime(2023, 1, 2, 19, 0, 0),
                                WindForce(30.0),
                            ),
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 19, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(40.0),
                            ),
                        ],
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 9, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindDirection([90.0, 90.0]),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_1B_4,
            ),
            (
                # Input Fingerprint: 333333332233333333333333
                # Type 2 group of size 2 between 2 type 3 groups => we will get only
                # one merged type 2 block
                # 1 WindForcePeriod, no WindDirectionPeriod
                generate_valid_times(periods=24),
                [30.0] * 8 + [15.0] * 2 + [31.0] * 14,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    )
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 333222222233333333333333
                # Max wind force is in the last type 3 group
                # 1 WindForcePeriod, no WindDirectionPeriod
                generate_valid_times(periods=24),
                [30.0] * 3 + [15.0] * 7 + [31.0] * 14,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 9, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 9, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 9, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                        flag=True,
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 322222222222222222222222
                # There is only one type 3 group with only one term.
                # 1 WindForcePeriod, no WindDirectionPeriod
                generate_valid_times(periods=24),
                [30.0] * 1 + [15.0] * 23,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 0, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 0, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 0, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 332222222222222222222222
                # There is only one type 3 group with 2 terms.
                # 1 WindForcePeriod, no WindDirectionPeriod
                generate_valid_times(periods=24),
                [30.0] * 2 + [15.0] * 22,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 1, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 1, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 1, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 333222222222222222222222
                # There is only one type 3 group with 3 terms.
                # 1 WindForcePeriod, no WindDirectionPeriod
                generate_valid_times(periods=24),
                [30.0] * 3 + [15.0] * 21,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 2, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 2, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 2, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 222222223223223223223223
                # 1 WindForcePeriod, no WindDirectionPeriod
                generate_valid_times(periods=24),
                [15.0] * 8 + [30.0, 15.0, 15.0] * 5 + [30.0],
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 7, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 7, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 7, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 222222223223223223223222
                # 1 WindForcePeriod, no WindDirectionPeriod
                generate_valid_times(periods=24),
                [15.0] * 8 + [30.0, 15.0, 15.0] * 5 + [15.0],
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 7, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 7, 0, 0),
                        Datetime(2023, 1, 2, 20, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 7, 0, 0),
                                Datetime(2023, 1, 2, 20, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 20, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 222322322322322322222222
                # The 1st group is a short type 2 group.
                # 1 WindForcePeriod, no WindDirectionPeriod
                generate_valid_times(periods=24),
                [15.0] * 3 + [30.0, 15.0, 15.0] * 5 + [15.0] * 6,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 2, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 2, 0, 0),
                        Datetime(2023, 1, 2, 15, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 2, 0, 0),
                                Datetime(2023, 1, 2, 15, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 15, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 32222222222222222222222
                # Only the 1st term has the type 3.
                # 1 WindForcePeriod, no WindDirectionPeriod
                generate_valid_times(periods=24),
                [30.0] * 1 + [15.0] * 23,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 0, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 0, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 0, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 22222222222222222222223
                # Only the last term has the type 3.
                # 1 WindForcePeriod, no WindDirectionPeriod
                generate_valid_times(periods=24),
                [15.0] * 23 + [30.0] * 1,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 22, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 22, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 22, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 333322222233333333333333
                # Max wind force is in the last type 3 group.
                generate_valid_times(periods=24),
                [30.0] * 4 + [15.0] * 6 + [31.0] * 14,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 3, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 3, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 3, 0, 0),
                        Datetime(2023, 1, 2, 9, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 9, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 9, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_2B_10,
            ),
            (
                # Input Fingerprint: 333222222233333333333333
                # Max wind force is in the 1st type 3 group
                generate_valid_times(periods=24),
                [35.0] * 3 + [15.0] * 7 + [30.0] * 14,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 2, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 2, 0, 0),
                                WindForce(35.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 2, 0, 0),
                        Datetime(2023, 1, 2, 9, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 9, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 9, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_2B_30,
            ),
            (
                # Input Fingerprint: 333222222233333333333333
                # Max wind force is in all type 3 group
                # 1 WindForcePeriod, no WindDirectionPeriod
                generate_valid_times(periods=24),
                [31.0] * 3 + [15.0] * 7 + [31.0] * 14,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 2, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 2, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 2, 0, 0),
                        Datetime(2023, 1, 2, 9, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 9, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 9, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_2B_10,
            ),
            (
                # Input Fingerprint: 22222222223222222222222
                # Max wind force is on the only one type 3 term
                generate_valid_times(periods=24),
                [15.0] * 10 + [31.0] * 1 + [15.0] * 13,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 9, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 9, 0, 0),
                        Datetime(2023, 1, 2, 10, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 9, 0, 0),
                                Datetime(2023, 1, 2, 10, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 10, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 333322222233333322223333
                # Max wind force is in the first type 3 group
                # There are 3 type 3 blocks => the 2 last are the closest and will be
                # merged. So there will stay only 2 type 3 blocks.
                generate_valid_times(periods=24),
                [32.0] * 4 + [15.0] * 6 + [31.0] * 6 + [15.0] * 4 + [31.0] * 4,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 3, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 3, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 3, 0, 0),
                        Datetime(2023, 1, 2, 9, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 9, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 9, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_2B_10,
            ),
            (
                # Input Fingerprint: 333322222233333322223333
                # Max wind force is in all type 3 group
                # 1 WindForcePeriod, no WindDirectionPeriod
                # There are 3 type 3 blocks => the 2 last are the closest and will be
                # merged. So there will stay only 2 type 3 blocks.
                generate_valid_times(periods=24),
                [31.0] * 4 + [15.0] * 6 + [31.0] * 6 + [15.0] * 4 + [31.0] * 4,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 3, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 3, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 3, 0, 0),
                        Datetime(2023, 1, 2, 9, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 9, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 9, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_2B_10,
            ),
            (
                # Input Fingerprint: 222222222333222222222223
                # Max wind force is in 1st type 3 group
                # 1 WindForcePeriod, no WindDirectionPeriod
                # There will stay 1 type 3 block.
                generate_valid_times(periods=24),
                [15.0] * 9 + [31.0] * 3 + [15.0] * 11 + [30.0] * 1,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 8, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 8, 0, 0),
                        Datetime(2023, 1, 2, 11, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 8, 0, 0),
                                Datetime(2023, 1, 2, 11, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 11, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 333333333333333333333333
                # All terms are of type 3
                # 1 WindForcePeriod, same WindDirection in the 1st and the last
                # WindDirectionPeriod
                generate_valid_times(periods=24),
                [30.0] * 24,
                [0.1] * 4 + [157.6] * 12 + [0.1] * 8,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindDirection([0.1]),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_1B_1,
            ),
            (
                # Input Fingerprint: 333333333333333333333333
                # All terms are of type 3
                # 1 WindForcePeriod, the 1st and the last WindDirection are opposite
                generate_valid_times(periods=24),
                [30.0] * 24,
                [180.0] * 4 + [157.6] * 12 + [0.1] * 8,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                        wd_periods=[],
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 322222222333222222222222
                # Max wind force is in 2nd type 3 group
                # 1 WindForcePeriod, no WindDirectionPeriod
                # There will stay 1 type 3 block.
                generate_valid_times(periods=24),
                [30.0] * 1 + [15.0] * 8 + [31.0] * 3 + [15.0] * 12,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 8, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 8, 0, 0),
                        Datetime(2023, 1, 2, 11, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 8, 0, 0),
                                Datetime(2023, 1, 2, 11, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 11, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 322222222333222222222222
                # Max wind force is in the 2nd type 3 blocks
                # 1 WindForcePeriod, no WindDirectionPeriod, 1 flagged WindBlocks
                generate_valid_times(periods=24),
                [30.0] * 1 + [15.0] * 8 + [41.0] * 3 + [15.0] * 12,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 8, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 8, 0, 0),
                        Datetime(2023, 1, 2, 11, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 8, 0, 0),
                                Datetime(2023, 1, 2, 11, 0, 0),
                                WindForce(40.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 11, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 22233222
                # 3h step between terms
                # 1 WindForcePeriod, no WindDirectionPeriod
                # There will stay 1 type 3 block.
                generate_valid_times(periods=8, freq="3H"),
                [15.0] * 3 + [30.0] * 2 + [16.0] * 3,
                [np.nan] * 3 + [0.1] * 1 + [157.6] * 1 + [np.nan] * 3,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 21, 0, 0),
                        Datetime(2023, 1, 2, 6, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 6, 0, 0),
                        Datetime(2023, 1, 2, 12, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 6, 0, 0),
                                Datetime(2023, 1, 2, 12, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 6, 0, 0),
                                Datetime(2023, 1, 2, 9, 0, 0),
                                WindDirection([0.1]),
                            ),
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 9, 0, 0),
                                Datetime(2023, 1, 2, 12, 0, 0),
                                WindDirection([157.5]),
                            ),
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 12, 0, 0),
                        Datetime(2023, 1, 2, 21, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                ],
                WindCase.CASE_3_1B_2,
            ),
            (
                # Input Fingerprint: 222222222222222333333
                # 3h step between terms
                # 1 WindForcePeriod, no WindDirectionPeriod
                # There will stay 1 type 3 block.
                generate_valid_times_v2("2023-01-02", (16, "H"), (5, "3H")),
                [15.0] * 15 + [30.0] * 6,
                [0.1] * 21,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 14, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 14, 0, 0),
                                WindDirection([0.1]),
                            ),
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 14, 0, 0),
                        Datetime(2023, 1, 3, 6, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 14, 0, 0),
                                Datetime(2023, 1, 3, 6, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 14, 0, 0),
                                Datetime(2023, 1, 3, 6, 0, 0),
                                WindDirection([0.1]),
                            ),
                        ],
                    ),
                ],
                WindCase.CASE_3_1B_1,
            ),
            (
                # Input Fingerprint: 333322222222222222222322
                # => WindBlocks: 32
                generate_valid_times(periods=24),
                [31.0] * 4 + [15.0] * 17 + [30.0] * 1 + [15.0] * 2,
                [0.1] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 3, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 3, 0, 0),
                                WindForce(31.0),
                            )
                        ],
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 3, 0, 0),
                                WindDirection([0.1]),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 3, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 3, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindDirection([0.1]),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_1B_1,
            ),
            (
                # Input Fingerprint: 333322222222222222223222
                # the max in on the 2nd type 3 block
                # => WindBlocks: 3232
                generate_valid_times(periods=24),
                [30.0] * 4 + [15.0] * 16 + [31.0] * 1 + [15.0] * 3,
                [0.1] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 3, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 3, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 3, 0, 0),
                                WindDirection([0.1]),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 3, 0, 0),
                        Datetime(2023, 1, 2, 19, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 3, 0, 0),
                                Datetime(2023, 1, 2, 19, 0, 0),
                                WindDirection([0.1]),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 19, 0, 0),
                        Datetime(2023, 1, 2, 20, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 19, 0, 0),
                                Datetime(2023, 1, 2, 20, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 20, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 20, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindDirection([0.1]),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_2B_3,
            ),
            (
                # Input Fingerprint: 2323233332323222
                # => WindBlocks 232
                generate_valid_times(periods=16),
                [15.0] + [30.0, 15.0] * 2 + [34.0] * 4 + [15.0, 30.0] * 2 + [15.0] * 3,
                [0.1] * 16,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 0, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 0, 0, 0),
                        Datetime(2023, 1, 2, 12, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 0, 0, 0),
                                Datetime(2023, 1, 2, 12, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 0, 0, 0),
                                Datetime(2023, 1, 2, 12, 0, 0),
                                WindDirection([0.1]),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 12, 0, 0),
                        Datetime(2023, 1, 2, 15, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 12, 0, 0),
                                Datetime(2023, 1, 2, 15, 0, 0),
                                WindDirection([0.1]),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_1B_1,
            ),
            (
                # Input Fingerprint: only one term of type 3 => 1 WindBlocks 3
                generate_valid_times(periods=1),
                [60.0],
                [0.1],
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 0, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 0, 0, 0),
                                WindForce(60.0),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 333222222222333333333222222222333333
                # The 2 first WindBlocks should be merged
                generate_valid_times(periods=36),
                [80.0] * 3 + [20.0] * 9 + [70.0] * 9 + [20.0] * 9 + [80.0] * 6,
                [np.nan] * 36,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 20, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 2, 0, 0),
                                WindForce(80.0),
                            ),
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 11, 0, 0),
                                Datetime(2023, 1, 2, 20, 0, 0),
                                WindForce(70.0),
                            ),
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 20, 0, 0),
                        Datetime(2023, 1, 3, 5, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 3, 5, 0, 0),
                        Datetime(2023, 1, 3, 11, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 3, 5, 0, 0),
                                Datetime(2023, 1, 3, 11, 0, 0),
                                WindForce(80.0),
                            ),
                        ],
                    ),
                ],
                WindCase.CASE_3_2B_40,
            ),
            (
                # Input Fingerprint: 333111111111333333333111111111333333
                # The type 1 terms are not taken in account => 1 type 3 WindBlock
                # TODO: this test should have the same result as the previous one => it
                #  could be a good code improvement
                generate_valid_times(periods=36),
                [80.0] * 3 + [1.0] * 9 + [70.0] * 9 + [1.0] * 9 + [80.0] * 6,
                [np.nan] * 36,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 3, 11, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 2, 0, 0),
                                WindForce(80.0),
                            ),
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 11, 0, 0),
                                Datetime(2023, 1, 2, 20, 0, 0),
                                WindForce(70.0),
                            ),
                            WindForcePeriod(
                                Datetime(2023, 1, 3, 5, 0, 0),
                                Datetime(2023, 1, 3, 11, 0, 0),
                                WindForce(80.0),
                            ),
                        ],
                    ),
                ],
                WindCase.CASE_3_1B_13,
            ),
            (
                # Input Fingerprint: 333222222233333333333333
                # Max wind force is in the last type 3 group
                # 1 WindForcePeriod, no WindDirectionPeriod
                generate_valid_times(periods=24),
                [30.0] * 3 + [15.0] * 7 + [41.0] * 14,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 9, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 9, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 9, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(40.0),
                            )
                        ],
                        flag=True,
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 333222222233333333333333
                # Max wind force is in the 1st type 3 block
                generate_valid_times(periods=24),
                [34.0] * 3 + [15.0] * 7 + [31.0] * 14,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 2, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 2, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 2, 0, 0),
                        Datetime(2023, 1, 2, 9, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 9, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 9, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_2B_10,
            ),
            (
                # Input Fingerprint: 333322222233333322223333
                # There are 3 type 3 blocks => the 2 last are the closest and will be
                # merged. So there will stay only 2 type 3 blocks.
                generate_valid_times(periods=24),
                [31.0] * 4 + [15.0] * 6 + [31.0] * 6 + [15.0] * 4 + [34.9] * 4,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 3, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 3, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 3, 0, 0),
                        Datetime(2023, 1, 2, 9, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 9, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 9, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_2B_10,
            ),
            (
                # Input Fingerprint: 222222222333222222222223
                # Max wind force is in 1st type 3 group
                # 1 WindForcePeriod, no WindDirectionPeriod
                # There will stay the 1st type 3 block.
                generate_valid_times(periods=24),
                [15.0] * 9 + [41.0] * 3 + [15.0] * 11 + [30.0] * 1,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 8, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 8, 0, 0),
                        Datetime(2023, 1, 2, 11, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 8, 0, 0),
                                Datetime(2023, 1, 2, 11, 0, 0),
                                WindForce(40.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 11, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                ],
                WindCase.CASE_3_1B_3,
            ),
            (
                # Input Fingerprint: 322222222333222222222222
                # Max wind force is in the 2 type 3 blocks
                # 1 WindForcePeriod, no WindDirectionPeriod, 2 flagged WindBlocks
                generate_valid_times(periods=24),
                [31.0] * 1 + [15.0] * 8 + [31.0] * 3 + [15.0] * 12,
                [np.nan] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 0, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 0, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 0, 0, 0),
                        Datetime(2023, 1, 2, 8, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 8, 0, 0),
                        Datetime(2023, 1, 2, 11, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 8, 0, 0),
                                Datetime(2023, 1, 2, 11, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 11, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                    ),
                ],
                WindCase.CASE_3_2B_10,
            ),
            (
                # Input Fingerprint: 333322222222222222222322
                # Max wind force is in the 1st type 3 block
                # => WindBlocks: 32
                generate_valid_times(periods=24),
                [41.0] * 4 + [15.0] * 17 + [30.0] * 1 + [15.0] * 2,
                [0.1] * 24,
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 23, 0, 0),
                        Datetime(2023, 1, 2, 3, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 3, 0, 0),
                                WindForce(41.0),
                            )
                        ],
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 1, 23, 0, 0),
                                Datetime(2023, 1, 2, 3, 0, 0),
                                WindDirection([0.1]),
                            )
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 3, 0, 0),
                        Datetime(2023, 1, 2, 23, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 3, 0, 0),
                                Datetime(2023, 1, 2, 23, 0, 0),
                                WindDirection([0.1]),
                            )
                        ],
                    ),
                ],
                WindCase.CASE_3_1B_1,
            ),
        ],
    )
    def test_block_builder_grid_1x1(
        self, valid_times, data_wf, data_wd, blocks_exp, case_exp
    ):
        """Test resulting WindBlocks built from 1x1 grid data."""
        composite = CompositeFactory1x1.get_composite_when_term_data_is_one_number(
            valid_times=valid_times,
            data_wind=data_wf,
            data_dir=data_wd,
        )
        self.check_block_builder(composite, blocks_exp, case_exp)

    @pytest.mark.parametrize(
        "valid_times, data_wf, data_wd, blocks_exp, case_exp",
        [
            (
                # Input Fingerprint: 23
                # 3h step between terms
                # The Q95 max of the type 3 block is 30. (and not 65. which are
                # in the type 2 block)
                generate_valid_times_v2("2023-01-02", (2, "3H")),
                [
                    [
                        [14.0, 15.0, 15.0, 15.0],
                        [15.0, 15.0, 15.0, 15.0],
                        [15.0, 15.0, 15.0, 15.0],
                        [15.0, 15.0, 15.0, 15.0],
                        [15.0, 15.0, 15.0, 15.0],
                        [15.0, 15.0, 15.0, 65.0],
                    ],
                    [
                        [29.0, 30.0, 30.0, 30.0],
                        [30.0, 30.0, 30.0, 30.0],
                        [30.0, 30.0, 30.0, 30.0],
                        [30.0, 30.0, 30.0, 30.0],
                        [30.0, 30.0, 30.0, 30.0],
                        [30.0, 30.0, 30.0, 31.0],
                    ],
                ],
                [
                    np.full((6, 4), 0.1),
                    np.full((6, 4), 157.5),
                ],
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 21, 0, 0),
                        Datetime(2023, 1, 2, 0, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 1, 21, 0, 0),
                                Datetime(2023, 1, 2, 0, 0, 0),
                                WindDirection([0.1]),
                            ),
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 0, 0, 0),
                        Datetime(2023, 1, 2, 3, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 0, 0, 0),
                                Datetime(2023, 1, 2, 3, 0, 0),
                                WindForce(30.0),
                            )
                        ],
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 0, 0, 0),
                                Datetime(2023, 1, 2, 3, 0, 0),
                                WindDirection([157.5]),
                            ),
                        ],
                    ),
                ],
                WindCase.CASE_3_1B_1,
            ),
            (
                # Input Fingerprint: 323
                # 3h step between terms
                # The Q95 max of the type 3 block is 56.85. (and not 60. which are
                # in the 1st type 3 block)
                generate_valid_times_v2("2023-01-02", (1, "2H"), (1, "3H"), (1, "4H")),
                [
                    [
                        [30.0, 30.0, 30.0, 30.0],
                        [30.0, 30.0, 30.0, 30.0],
                        [30.0, 30.0, 30.0, 30.0],
                        [30.0, 30.0, 30.0, 30.0],
                        [30.0, 30.0, 30.0, 30.0],
                        [30.0, 30.0, 30.0, 60.0],
                    ],  # Q95 = 30.0
                    [
                        [16.0, 16.0, 16.0, 16.0],
                        [16.0, 16.0, 16.0, 16.0],
                        [16.0, 16.0, 16.0, 16.0],
                        [16.0, 16.0, 16.0, 16.0],
                        [16.0, 16.0, 16.0, 16.0],
                        [16.0, 16.0, 16.0, 65.0],
                    ],  #
                    [
                        [50.0, 50.0, 50.0, 50.0],
                        [50.0, 50.0, 50.0, 50.0],
                        [50.0, 50.0, 50.0, 50.0],
                        [50.0, 50.0, 50.0, 50.0],
                        [50.0, 50.0, 50.0, 50.0],
                        [55.0, 56.0, 57.0, 58.0],
                    ],  # Q95 = 56.85
                ],
                [
                    np.full((6, 4), 0.1),
                    np.full((6, 4), 157.5),
                    np.full((6, 4), 157.5),
                ],
                [
                    WindBlock(
                        Datetime(2023, 1, 1, 21, 0, 0),
                        Datetime(2023, 1, 2, 3, 0, 0),
                        WindType.TYPE_2,
                        flag=False,
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 1, 21, 0, 0),
                                Datetime(2023, 1, 2, 0, 0, 0),
                                WindDirection([0.1]),
                            ),
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 0, 0, 0),
                                Datetime(2023, 1, 2, 3, 0, 0),
                                WindDirection([157.5]),
                            ),
                        ],
                    ),
                    WindBlock(
                        Datetime(2023, 1, 2, 3, 0, 0),
                        Datetime(2023, 1, 2, 7, 0, 0),
                        WindType.TYPE_3,
                        flag=True,
                        wf_periods=[
                            WindForcePeriod(
                                Datetime(2023, 1, 2, 3, 0, 0),
                                Datetime(2023, 1, 2, 7, 0, 0),
                                WindForce(55.0),
                            )
                        ],
                        wd_periods=[
                            WindDirectionPeriod(
                                Datetime(2023, 1, 2, 3, 0, 0),
                                Datetime(2023, 1, 2, 7, 0, 0),
                                WindDirection([157.5]),
                            ),
                        ],
                    ),
                ],
                WindCase.CASE_3_1B_1,
            ),
        ],
    )
    def test_block_builder_grid_6x2(
        self, valid_times, data_wf, data_wd, blocks_exp, case_exp
    ):
        """Test resulting WindBlocks built from 6x2 grid data."""
        composite = CompositeFactory6x4.get(
            valid_times=valid_times,
            data_wind=data_wf,
            data_dir=data_wd,
        )
        self.check_block_builder(composite, blocks_exp, case_exp)

    @pytest.mark.parametrize(
        "valid_times, data_wf",
        [
            (
                generate_valid_times("2023-01-02", 3),
                [
                    [
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 65.0],
                    ],
                    [
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 25.0, 30.0, 60.0],
                    ],  # Q95 of filtered data is 57.0
                    [
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 1.0, 1.0, 1.0],
                        [1.0, 25.0, 30.0, 32.0],
                    ],  # Q95 of filtered data is 31.8
                ],
            )
        ],
    )
    def test_block_builder_q95_max_6x4(self, valid_times, data_wf):
        """Test resulting WindBlocks built from 6x2 grid data."""
        composite = CompositeFactory6x4.get(
            valid_times=valid_times,
            data_wind=data_wf,
        )

        # Create master summary builder, specially to filter the data
        summary_builder = self.create_master_summary_builder_from_composite(composite)

        case3_summary_builder: Case3SummaryBuilder = Case3SummaryBuilder(
            summary_builder.pd_summary, summary_builder.data_wd, summary_builder.data_wf
        )
        case3_summary_builder.run(Datetime(datetime.now()))

        pd_data = summary_builder.pd_summary.data
        values_to_test = pd_data[summary_builder.pd_summary.COL_WFQ].values
        np.array_equal(
            values_to_test.astype(np.float64),
            np.array([np.nan, 57.0, 31.8]),
            equal_nan=True,
        )
        assert pd_data.attrs[summary_builder.pd_summary.WFQ_MAX] == 57.0

    @pytest.mark.parametrize(
        "valid_times, data_wf, data_wd",
        [
            (
                # Input Fingerprint: 111111222222222222222222 => no type 3 terms
                generate_valid_times(periods=24),
                [10.0] * 6 + [15.0] * 18,
                [np.nan] * 24,
            ),
        ],
    )
    def test_summary_builder_error(self, valid_times, data_wf, data_wd):
        reference_datetime: Datetime = Datetime(datetime.now())
        composite = CompositeFactory1x1.get_composite_when_term_data_is_one_number(
            valid_times=valid_times,
            data_wind=data_wf,
            data_dir=data_wd,
        )
        summary_builder = self.create_master_summary_builder_from_composite(composite)

        with pytest.raises(WindSynthesisError):
            case3_summary_builder: Case3SummaryBuilder = Case3SummaryBuilder(
                summary_builder.pd_summary,
                summary_builder.data_wd,
                summary_builder.data_wf,
            )
            case3_summary_builder.run(reference_datetime)


class TestGenerateSummaryError(TestGenerateSummary):
    class CompositeFactory(CompositeFactory2x2):
        LON = [30, 31]
        LAT = [40, 41]

    def get_summary(self, wind_summary_builder_class) -> dict:
        valid_times = generate_valid_times(periods=1)

        composite = self.CompositeFactory().get(
            valid_times=valid_times, data_wind=np.full((2, 2), 10.0)
        )
        dataset = composite.compute()
        summary_builder = wind_summary_builder_class(composite, dataset)
        reference_datetime: Datetime = Datetime(datetime.now())
        summary = summary_builder.compute(reference_datetime)

        return summary

    def test_summary_with_error_case(self):

        for error in WindSummaryBuilder.CACHED_EXCEPTIONS:

            class BadWindSummaryBuilder(WindSummaryBuilder):
                def _generate_summary(self, reference_datetime: Datetime) -> None:
                    raise error

            summary = self.get_summary(BadWindSummaryBuilder)
            assert summary["wind"]["case"] == ERROR_CASE
            assert summary["wind"].get("msg") is not None

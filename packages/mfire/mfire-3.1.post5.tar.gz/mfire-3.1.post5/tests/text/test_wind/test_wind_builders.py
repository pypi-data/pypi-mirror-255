import pytest

from mfire.text.wind.builders import GustParamBuilder, WindBuilder, WindParamBuilder
from mfire.text.wind.const import ERROR_CASE


class TestWindBuilder:
    @staticmethod
    def check_builder_with_bad_summary(summary: dict, builder_class):
        builder = builder_class()
        text, _ = builder.compute(summary)

        assert text == "Erreur dans la génération des synthèses de vent."

    @staticmethod
    def check_builder(summary: dict, builder_class, assert_equals_result):
        builder = builder_class()
        text, _ = builder.compute(summary)

        assert_equals_result(text)

    @pytest.mark.parametrize(
        "summary",
        [
            (
                {
                    "params": {
                        "gust": {
                            "case": "gust_case_2",
                            "units": "km/h",
                            "gust_interval": (50, 60),
                        },
                        "wind": {"case": "unknown_case"},
                    }
                }
            ),
            (
                {
                    "params": {
                        "gust": {
                            "case": "gust_case_2",
                            "units": "km/h",
                            "gust_interval": (50, 60),
                        },
                        "wind": {"case": ERROR_CASE},
                    }
                }
            ),
            (
                {
                    "params": {
                        "gust": {
                            "case": "gust_case_2",
                            "units": "km/h",
                            "gust_interval": (50, 60),
                        },
                        "wind": {"unknown_selector": "wind_case_2"},
                    }
                }
            ),
            (
                {
                    "params": {
                        "gust": {"case": "unknown_case"},
                        "wind": {
                            "case": "wind_case_2",
                            "units": "km/h",
                            "wf_intensity": "modéré",
                            "wd_periods": [],
                        },
                    }
                }
            ),
            (
                {
                    "params": {
                        "gust": {"case": ERROR_CASE},
                        "wind": {
                            "case": "wind_case_2",
                            "units": "km/h",
                            "wf_intensity": "modéré",
                            "wd_periods": [],
                        },
                    }
                }
            ),
            (
                {
                    "params": {
                        "gust": {"unknown_selector": "gust_case_2"},
                        "wind": {
                            "case": "wind_case_2",
                            "units": "km/h",
                            "wf_intensity": "modéré",
                            "wd_periods": [],
                        },
                    }
                }
            ),
            (
                {
                    "params": {
                        "wind": {
                            "case": "wind_case_2",
                            "units": "km/h",
                            "wf_intensity": "modéré",
                            "wd_periods": [],
                        }
                    }
                }
            ),
            (
                {
                    "params": {
                        "gust": {
                            "case": "gust_case_2",
                            "units": "km/h",
                            "gust_interval": (50, 60),
                        },
                    }
                }
            ),
        ],
    )
    def test_wind_builder_with_bad_summary(self, summary):
        self.check_builder_with_bad_summary(summary, WindBuilder)

    @pytest.mark.parametrize(
        "summary",
        [
            {"case": "unknown_case"},
            {"case": ERROR_CASE},
            {"unknown_selector": "wind_case_2"},
        ],
    )
    def test_wind_param_builder_with_bad_summary(self, summary):
        self.check_builder_with_bad_summary(summary, WindParamBuilder)

    @pytest.mark.parametrize(
        "summary",
        [
            {"case": "unknown_case"},
            {"case": ERROR_CASE},
            {"unknown_selector": "gust_case_2"},
        ],
    )
    def test_gust_param_builder_with_bad_summary(self, summary):
        self.check_builder_with_bad_summary(summary, GustParamBuilder)

    def test_wind_builder(self, assert_equals_result):

        summary = {
            "params": {
                "gust": {
                    "case": "gust_case_2",
                    "units": "km/h",
                    "gust_interval": (50, 60),
                    "force_min": 50,
                    "gust_tempos": (None, "lundi après-midi"),
                },
                "wind": {
                    "case": "wind_case_2",
                    "units": "km/h",
                    "wf_intensity": "modéré",
                    "wd_periods": [],
                },
            }
        }

        self.check_builder(summary, WindBuilder, assert_equals_result)

    def test_wind_param_builder(self, assert_equals_result):

        summary = {
            "case": "wind_case_2",
            "units": "km/h",
            "wf_intensity": "modéré",
            "wd_periods": [],
        }

        self.check_builder(summary, WindParamBuilder, assert_equals_result)

    def test_gust_param_builder(self, assert_equals_result):

        summary = {
            "case": "gust_case_2",
            "units": "km/h",
            "gust_interval": (50, 60),
            "force_min": 50,
            "gust_tempos": (None, "lundi après-midi"),
        }

        self.check_builder(summary, GustParamBuilder, assert_equals_result)

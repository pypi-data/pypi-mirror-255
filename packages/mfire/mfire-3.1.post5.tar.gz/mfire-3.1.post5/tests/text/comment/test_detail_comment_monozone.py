"""test_detail_comment.py

Unit tests of the text.detail_comment module.
"""

import numpy as np
import pytest

import mfire.utils.mfxarray as xr
from mfire.composite import (
    Aggregation,
    EventComposite,
    FieldComposite,
    LevelComposite,
    LocalisationConfig,
    Period,
    RiskComponentComposite,
)
from mfire.settings.constants import SETTINGS_DIR
from mfire.text.comment import Reducer
from mfire.text.comment.monozone import Monozone

tempe_final_risk = {
    "dims": ("valid_time",),
    "attrs": {
        "long_name": "2 metre temperature",
        "units": "K",
        "standard_name": "air_temperature",
        "PROMETHEE_z_ref": "franxl1s100",
    },
    "data": [
        2.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
    ],
    "coords": {
        "valid_time": {
            "dims": ("valid_time",),
            "data": [
                np.datetime64("2019-10-19T15:00:00.00"),
                np.datetime64("2019-10-19T16:00:00.00"),
                np.datetime64("2019-10-19T17:00:00.00"),
                np.datetime64("2019-10-19T18:00:00.00"),
                np.datetime64("2019-10-19T19:00:00.00"),
                np.datetime64("2019-10-19T20:00:00.00"),
                np.datetime64("2019-10-19T21:00:00.00"),
                np.datetime64("2019-10-19T22:00:00.00"),
                np.datetime64("2019-10-19T23:00:00.00"),
                np.datetime64("2019-10-20T00:00:00.00"),
                np.datetime64("2019-10-20T01:00:00.00"),
                np.datetime64("2019-10-20T02:00:00.00"),
                np.datetime64("2019-10-20T03:00:00.00"),
                np.datetime64("2019-10-20T04:00:00.00"),
                np.datetime64("2019-10-20T05:00:00.00"),
                np.datetime64("2019-10-20T06:00:00.00"),
                np.datetime64("2019-10-20T07:00:00.00"),
                np.datetime64("2019-10-20T08:00:00.00"),
                np.datetime64("2019-10-20T09:00:00.00"),
                np.datetime64("2019-10-20T10:00:00.00"),
                np.datetime64("2019-10-20T11:00:00.00"),
                np.datetime64("2019-10-20T12:00:00.00"),
                np.datetime64("2019-10-20T13:00:00.00"),
                np.datetime64("2019-10-20T14:00:00.00"),
            ],
        },
        "id": {"dims": (), "data": "b5f2f01e-a414-4920-90bb-6702a1ddae24"},
        "areaName": {"dims": (), "data": "sur tout le département"},
    },
}


tempe_general = {
    "coords": {
        "risk_level": {"dims": ("risk_level",), "data": [1, 2, 3]},
        "valid_time": {
            "dims": ("valid_time",),
            "data": [
                np.datetime64("2019-10-19T15:00:00.00"),
                np.datetime64("2019-10-19T16:00:00.00"),
                np.datetime64("2019-10-19T17:00:00.00"),
                np.datetime64("2019-10-19T18:00:00.00"),
                np.datetime64("2019-10-19T19:00:00.00"),
                np.datetime64("2019-10-19T20:00:00.00"),
                np.datetime64("2019-10-19T21:00:00.00"),
                np.datetime64("2019-10-19T22:00:00.00"),
                np.datetime64("2019-10-19T23:00:00.00"),
                np.datetime64("2019-10-20T00:00:00.00"),
                np.datetime64("2019-10-20T01:00:00.00"),
                np.datetime64("2019-10-20T02:00:00.00"),
                np.datetime64("2019-10-20T03:00:00.00"),
                np.datetime64("2019-10-20T04:00:00.00"),
                np.datetime64("2019-10-20T05:00:00.00"),
                np.datetime64("2019-10-20T06:00:00.00"),
                np.datetime64("2019-10-20T07:00:00.00"),
                np.datetime64("2019-10-20T08:00:00.00"),
                np.datetime64("2019-10-20T09:00:00.00"),
                np.datetime64("2019-10-20T10:00:00.00"),
                np.datetime64("2019-10-20T11:00:00.00"),
                np.datetime64("2019-10-20T12:00:00.00"),
                np.datetime64("2019-10-20T13:00:00.00"),
                np.datetime64("2019-10-20T14:00:00.00"),
            ],
        },
        "id": {"dims": (), "data": "b5f2f01e-a414-4920-90bb-6702a1ddae24"},
        "areaName": {"dims": (), "data": "sur tout le département"},
        "evt": {"dims": ("evt",), "data": [0]},
    },
    "dims": {"risk_level": 3, "valid_time": 24, "evt": 1},
    "data_vars": {
        "min_plain": {
            "dims": ("risk_level", "evt", "valid_time"),
            "data": [
                [
                    [
                        11.8,
                        11.1,
                        10.4,
                        9.4,
                        9.0,
                        8.5,
                        8.1,
                        8.0,
                        8.0,
                        8.0,
                        8.0,
                        8.0,
                        7.9,
                        7.7,
                        7.4,
                        7.2,
                        8.1,
                        8.9,
                        9.2,
                        9.7,
                        10.2,
                        10.7,
                        10.6,
                        10.6,
                    ]
                ],
                [
                    [
                        11.8,
                        11.1,
                        10.4,
                        9.4,
                        9.0,
                        8.5,
                        8.1,
                        8.0,
                        8.0,
                        8.0,
                        8.0,
                        8.0,
                        7.9,
                        7.7,
                        7.4,
                        7.2,
                        8.1,
                        8.9,
                        9.2,
                        9.7,
                        10.2,
                        10.7,
                        10.6,
                        10.6,
                    ]
                ],
                [
                    [
                        11.8,
                        11.1,
                        10.4,
                        9.4,
                        9.0,
                        8.5,
                        8.1,
                        8.0,
                        8.0,
                        8.0,
                        8.0,
                        8.0,
                        7.9,
                        7.7,
                        7.4,
                        7.2,
                        8.1,
                        8.9,
                        9.2,
                        9.7,
                        10.2,
                        10.7,
                        10.6,
                        10.6,
                    ]
                ],
            ],
        },
        "max_plain": {
            "dims": ("risk_level", "evt", "valid_time"),
            "data": [
                [
                    [
                        15.2,
                        14.7,
                        14.7,
                        14.6,
                        14.5,
                        14.3,
                        14.2,
                        13.8,
                        13.5,
                        13.2,
                        12.9,
                        12.5,
                        12.1,
                        12.4,
                        12.6,
                        12.9,
                        13.1,
                        13.3,
                        14.0,
                        13.9,
                        14.0,
                        14.3,
                        14.2,
                        14.1,
                    ]
                ],
                [
                    [
                        15.2,
                        14.7,
                        14.7,
                        14.6,
                        14.5,
                        14.3,
                        14.2,
                        13.8,
                        13.5,
                        13.2,
                        12.9,
                        12.5,
                        12.1,
                        12.4,
                        12.6,
                        12.9,
                        13.1,
                        13.3,
                        14.0,
                        13.9,
                        14.0,
                        14.3,
                        14.2,
                        14.1,
                    ]
                ],
                [
                    [
                        15.2,
                        14.7,
                        14.7,
                        14.6,
                        14.5,
                        14.3,
                        14.2,
                        13.8,
                        13.5,
                        13.2,
                        12.9,
                        12.5,
                        12.1,
                        12.4,
                        12.6,
                        12.9,
                        13.1,
                        13.3,
                        14.0,
                        13.9,
                        14.0,
                        14.3,
                        14.2,
                        14.1,
                    ]
                ],
            ],
        },
        "rep_value_plain": {
            "dims": ("risk_level", "evt", "valid_time"),
            "data": [
                [
                    [
                        15.2,
                        14.7,
                        14.7,
                        14.6,
                        14.5,
                        14.3,
                        14.2,
                        13.8,
                        13.5,
                        13.2,
                        12.9,
                        12.5,
                        12.1,
                        12.4,
                        12.6,
                        12.9,
                        13.1,
                        13.3,
                        14.0,
                        13.9,
                        14.0,
                        14.3,
                        14.2,
                        14.1,
                    ]
                ],
                [
                    [
                        15.2,
                        14.7,
                        14.7,
                        14.6,
                        14.5,
                        14.3,
                        14.2,
                        13.8,
                        13.5,
                        13.2,
                        12.9,
                        12.5,
                        12.1,
                        12.4,
                        12.6,
                        12.9,
                        13.1,
                        13.3,
                        14.0,
                        13.9,
                        14.0,
                        14.3,
                        14.2,
                        14.1,
                    ]
                ],
                [
                    [
                        15.2,
                        14.7,
                        14.7,
                        14.6,
                        14.5,
                        14.3,
                        14.2,
                        13.8,
                        13.5,
                        13.2,
                        12.9,
                        12.5,
                        12.1,
                        12.4,
                        12.6,
                        12.9,
                        13.1,
                        13.3,
                        14.0,
                        13.9,
                        14.0,
                        14.3,
                        14.2,
                        14.1,
                    ]
                ],
            ],
        },
        "weatherVarName": {
            "dims": ("risk_level", "evt"),
            "data": [["T__HAUTEUR2"], ["T__HAUTEUR2"], ["T__HAUTEUR2"]],
        },
        "units": {
            "dims": ("risk_level", "evt"),
            "data": [["celsius"], ["celsius"], ["celsius"]],
        },
        "threshold_plain": {
            "dims": ("risk_level", "evt"),
            "data": [[13], [13], [13]],
        },
        "occurrence_event": {
            "dims": ("risk_level", "evt"),
            "data": [[True], [True], [True]],
        },
    },
}


pluie_final_risk = {
    "dims": ("valid_time",),
    "attrs": {
        "long_name": "2 metre temperature",
        "units": "K",
        "standard_name": "air_temperature",
        "PROMETHEE_z_ref": "franxl1s100",
    },
    "data": [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        3,
        3,
        3,
        1.0,
        1.0,
        1.0,
    ],
    "coords": {
        "valid_time": {
            "dims": ("valid_time",),
            "data": [
                np.datetime64("2019-11-17T15:00:00.00"),
                np.datetime64("2019-11-17T16:00:00.00"),
                np.datetime64("2019-11-17T17:00:00.00"),
                np.datetime64("2019-11-17T18:00:00.00"),
                np.datetime64("2019-11-17T19:00:00.00"),
                np.datetime64("2019-11-17T20:00:00.00"),
                np.datetime64("2019-11-17T21:00:00.00"),
                np.datetime64("2019-11-17T22:00:00.00"),
                np.datetime64("2019-11-17T23:00:00.00"),
                np.datetime64("2019-11-18T00:00:00.00"),
                np.datetime64("2019-11-18T01:00:00.00"),
                np.datetime64("2019-11-18T02:00:00.00"),
                np.datetime64("2019-11-18T03:00:00.00"),
                np.datetime64("2019-11-18T04:00:00.00"),
                np.datetime64("2019-11-18T05:00:00.00"),
                np.datetime64("2019-11-18T06:00:00.00"),
                np.datetime64("2019-11-18T07:00:00.00"),
                np.datetime64("2019-11-18T08:00:00.00"),
                np.datetime64("2019-11-18T09:00:00.00"),
                np.datetime64("2019-11-18T10:00:00.00"),
                np.datetime64("2019-11-18T11:00:00.00"),
                np.datetime64("2019-11-18T12:00:00.00"),
                np.datetime64("2019-11-18T13:00:00.00"),
                np.datetime64("2019-11-18T14:00:00.00"),
            ],
        },
        "id": {"dims": (), "data": "e296d014-981b-412b-9c63-c3bd01d4dac0"},
        "areaName": {"dims": (), "data": "sur tout le département"},
    },
}


pluie_cumul = {
    "coords": {
        "risk_level": {"dims": ("risk_level",), "data": [1, 2, 3]},
        "valid_time": {
            "dims": ("valid_time",),
            "data": [
                np.datetime64("2019-11-17T15:00:00.00"),
                np.datetime64("2019-11-17T16:00:00.00"),
                np.datetime64("2019-11-17T17:00:00.00"),
                np.datetime64("2019-11-17T18:00:00.00"),
                np.datetime64("2019-11-17T19:00:00.00"),
                np.datetime64("2019-11-17T20:00:00.00"),
                np.datetime64("2019-11-17T21:00:00.00"),
                np.datetime64("2019-11-17T22:00:00.00"),
                np.datetime64("2019-11-17T23:00:00.00"),
                np.datetime64("2019-11-18T00:00:00.00"),
                np.datetime64("2019-11-18T01:00:00.00"),
                np.datetime64("2019-11-18T02:00:00.00"),
                np.datetime64("2019-11-18T03:00:00.00"),
                np.datetime64("2019-11-18T04:00:00.00"),
                np.datetime64("2019-11-18T05:00:00.00"),
                np.datetime64("2019-11-18T06:00:00.00"),
                np.datetime64("2019-11-18T07:00:00.00"),
                np.datetime64("2019-11-18T08:00:00.00"),
                np.datetime64("2019-11-18T09:00:00.00"),
                np.datetime64("2019-11-18T10:00:00.00"),
                np.datetime64("2019-11-18T11:00:00.00"),
                np.datetime64("2019-11-18T12:00:00.00"),
                np.datetime64("2019-11-18T13:00:00.00"),
                np.datetime64("2019-11-18T14:00:00.00"),
            ],
        },
        "id": {"dims": (), "data": "e296d014-981b-412b-9c63-c3bd01d4dac0"},
        "areaName": {"dims": (), "data": "sur tout le département"},
        "evt": {"dims": ("evt",), "data": [0]},
    },
    "dims": {"risk_level": 3, "valid_time": 24, "evt": 1},
    "data_vars": {
        "min_plain": {
            "dims": ("risk_level", "evt", "valid_time"),
            "data": [
                [
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.03,
                        0.03,
                        0.03,
                        0.12,
                        0.12,
                        0.12,
                        0.34,
                        0.34,
                        6.5,
                        7.4,
                        7.2,
                    ]
                ],
                [
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.03,
                        0.03,
                        0.03,
                        0.12,
                        0.12,
                        0.12,
                        0.34,
                        0.34,
                        6.5,
                        7.4,
                        7.2,
                    ]
                ],
                [
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.03,
                        0.03,
                        0.03,
                        0.12,
                        0.12,
                        0.12,
                        0.34,
                        0.34,
                        6.5,
                        7.4,
                        7.2,
                    ]
                ],
            ],
        },
        "max_plain": {
            "dims": ("risk_level", "evt", "valid_time"),
            "data": [
                [
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.10,
                        0.10,
                        0.10,
                        0.50,
                        0.50,
                        0.50,
                        3.96,
                        3.96,
                        3.96,
                        2.94,
                        2.94,
                        2.94,
                        2.31,
                        2.31,
                        2.31,
                        3.22,
                        3.22,
                        15.2,
                        15.5,
                        16,
                    ]
                ],
                [
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.10,
                        0.10,
                        0.10,
                        0.50,
                        0.50,
                        0.50,
                        3.96,
                        3.96,
                        3.96,
                        2.94,
                        2.94,
                        2.94,
                        2.31,
                        2.31,
                        2.31,
                        3.22,
                        3.22,
                        15.2,
                        15.5,
                        16,
                    ]
                ],
                [
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.10,
                        0.10,
                        0.10,
                        0.50,
                        0.50,
                        0.50,
                        3.96,
                        3.96,
                        3.96,
                        2.94,
                        2.94,
                        2.94,
                        2.31,
                        2.31,
                        2.31,
                        3.22,
                        3.22,
                        15.2,
                        15.5,
                        16,
                    ]
                ],
            ],
        },
        "rep_value_plain": {
            "dims": ("risk_level", "evt", "valid_time"),
            "data": [
                [
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.10,
                        0.10,
                        0.10,
                        0.50,
                        0.50,
                        0.50,
                        3.96,
                        3.96,
                        3.96,
                        2.94,
                        2.94,
                        2.94,
                        2.31,
                        2.31,
                        2.31,
                        3.22,
                        3.22,
                        15.2,
                        15.5,
                        16,
                    ]
                ],
                [
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.10,
                        0.10,
                        0.10,
                        0.50,
                        0.50,
                        0.50,
                        3.96,
                        3.96,
                        3.96,
                        2.94,
                        2.94,
                        2.94,
                        2.31,
                        2.31,
                        2.31,
                        3.22,
                        3.22,
                        15.2,
                        15.5,
                        16,
                    ]
                ],
                [
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.10,
                        0.10,
                        0.10,
                        0.50,
                        0.50,
                        0.50,
                        3.96,
                        3.96,
                        3.96,
                        2.94,
                        2.94,
                        2.94,
                        2.31,
                        2.31,
                        2.31,
                        3.22,
                        3.22,
                        15.2,
                        15.5,
                        16,
                    ]
                ],
            ],
        },
        "weatherVarName": {
            "dims": ("risk_level", "evt"),
            "data": [["EAU1__SOL"], ["EAU1__SOL"], ["EAU1__SOL"]],
        },
        "units": {"dims": ("risk_level", "evt"), "data": [["mm"], ["mm"], ["mm"]]},
        "threshold_plain": {
            "dims": ("risk_level", "evt"),
            "data": [[2], [2], [2]],
        },
        "occurrence_event": {
            "dims": ("risk_level", "evt"),
            "data": [[True], [True], [True]],
        },
    },
}


class TestMonozone:
    """Class for testing monozone comment builder."""

    @pytest.mark.filterwarnings("ignore: warnings")
    def test_monozone_general(self):
        """Testing a monozone comment case : general"""
        np.random.seed(1)
        final_risk_da = xr.DataArray.from_dict(tempe_final_risk)

        risk_ds = xr.Dataset.from_dict(tempe_general)

        sel = {
            "slice": {
                "valid_time": [
                    "2019-10-19T15:00:00.000000",
                    "2019-10-20T14:00:00.000000",
                ]
            }
        }
        field = FieldComposite(
            file="./data/20191019T0000/promethee/FRANXL1S100/T__HAUTEUR2.0013_0048_"
            "0001.netcdf",
            selection=sel,
            grid_name="franxl1s100",
            name="T__HAUTEUR2",
        )
        aggregation = Aggregation(method="requiredDensity", kwargs={"dr": 0.00})
        localisation = LocalisationConfig(compass_split=False, altitude_split=False)

        plain1 = {"threshold": 10, "comparison_op": "supegal", "units": "celsius"}
        element1 = EventComposite(
            category="quantitative",
            field=field,
            plain=plain1,
            altitude={"filename": SETTINGS_DIR / "geos/altitudes/franxl1s100.nc"},
            geos={"file": "toto.nc", "mask_id": "b5f2f01e-a414-4920-90bb-6702a1ddae24"},
        )

        level_1 = LevelComposite(
            level=1,
            probability="no",
            logical_op_list=[],
            aggregation_type="downStream",
            aggregation=aggregation,
            elements_event=[element1],
            localisation=localisation,
        )

        plain2 = {"threshold": 15, "comparison_op": "supegal", "units": "celsius"}
        element2 = EventComposite(
            category="quantitative",
            field=field,
            plain=plain2,
            altitude={"filename": SETTINGS_DIR / "geos/altitudes/franxl1s100.nc"},
            geos={"file": "toto.nc", "mask_id": "b5f2f01e-a414-4920-90bb-6702a1ddae24"},
        )

        level_2 = LevelComposite(
            level=2,
            probability="no",
            logical_op_list=[],
            aggregation_type="downStream",
            aggregation=aggregation,
            elements_event=[element2],
            localisation=localisation,
        )

        plain3 = {"threshold": 20, "comparison_op": "supegal", "units": "celsius"}
        element3 = EventComposite(
            category="quantitative",
            field=field,
            plain=plain3,
            altitude={"filename": SETTINGS_DIR / "geos/altitudes/franxl1s100.nc"},
            geos={"file": "toto.nc", "mask_id": "b5f2f01e-a414-4920-90bb-6702a1ddae24"},
        )

        level_3 = LevelComposite(
            level=3,
            probability="no",
            logical_op_list=[],
            aggregation_type="downStream",
            aggregation=aggregation,
            elements_event=[element3],
            localisation=localisation,
        )

        period = Period(
            id="751410a0-a404-45de-8548-1944af4c6e60",
            name="PROD+1h / PROD+24h",
            start="20191019T150000",
            stop="20191020T140000",
        )

        component = RiskComponentComposite(
            id="055f76ce-4f55-4c37-8284-2e0a165a88cb",
            name="tempe_for_test",
            production_id="afe389a0-145c-4836-8643-e2ad28b66dfc",
            production_name="Promethee_CD01",
            production_datetime="2019-10-19T14:00:00.000000",
            type="risk",
            levels=[level_1, level_2, level_3],
            hazard_id="334ec6b5-cde8-4306-80dd-d40badcc43a9",
            hazard_name="Chaleur",
            period=period,
            product_comment=True,
        )
        component._risks_ds = risk_ds
        component._final_risk_da = final_risk_da

        reducer = Reducer(component=component)
        reducer.module = "unizone"
        level_max = max(risk_ds.risk_level.values)
        risk_max = max(final_risk_da.values)
        risk_min = min(final_risk_da.values)

        # on test la normalization du risque
        norm_risk = final_risk_da.values
        if level_max > 1:
            norm_risk = np.where(
                norm_risk, 1 - (((level_max - norm_risk) * 0.5) / (level_max - 1)), 0
            )

        assert (
            norm_risk
            == [
                0.75,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
            ]
        ).all()

        # on teste la dtw : calul de distance et template
        reducer.compute_distance(norm_risk, method="first")
        assert reducer.reduction["centroid"] == (0.75,)
        assert (
            reducer.reduction["template"]
            == "Alerte durant toute la période de surveillance. {B0_val}."
        )

        # on teste la reduction du risque
        reduced_risk, reducer.reduction = reducer.reduce_risk(
            component.final_risk_da, component.risks_ds
        )
        reducer.reduction["risk_max"] = risk_max
        reducer.reduction["risk_min"] = risk_min
        reducer.reduction["level_maxi"] = level_max

        assert reduced_risk == [2]
        assert "B0" in reducer.reduction
        assert reducer.reduction["B0"]["T__HAUTEUR2"]["plain"]["units"] == "celsius"
        assert reducer.reduction["B0"]["T__HAUTEUR2"]["plain"]["min"] == 7.2

        # on teste les level_int level_max
        reducer.get_levels_val()
        assert reducer.reduction["level_int"]["T__HAUTEUR2"]["plain"]["max"] == 15.2
        assert not bool(reducer.reduction["level_max"])

        # on teste le builder
        builder = Monozone(reducer.reduction["template"])
        comment = builder.compute(reducer.reduction)
        assert (
            comment == "Alerte durant toute la période de surveillance. On attend une "
            "température aux alentours de 16°C."
        )

    @pytest.mark.filterwarnings("ignore: warnings")
    def test_monozone_cumuls(self):
        """Testing a monozone comment case : cumuls"""
        np.random.seed(1)
        final_risk_da = xr.DataArray.from_dict(pluie_final_risk)

        risk_ds = xr.Dataset.from_dict(pluie_cumul)

        sel = {
            "slice": {
                "valid_time": ["2019-11-17T15:00:00.00", "2019-11-18T14:00:00.00"]
            }
        }
        field = FieldComposite(
            file="./data/20191117T0000/promethee/FRANXL1S100/EAU1__SOL.0013_0048_"
            "0001.netcdf",
            selection=sel,
            grid_name="franxl1s100",
            name="EAU1__SOL",
        )
        aggregation = Aggregation(method="requiredDensity", kwargs={"dr": 0.00})
        localisation = LocalisationConfig(compass_split=False, altitude_split=False)

        plain1 = {"threshold": 1, "comparison_op": "supegal", "units": "mm"}
        element1 = EventComposite(
            category="quantitative",
            field=field,
            plain=plain1,
            altitude={"filename": SETTINGS_DIR / "geos/altitudes/franxl1s100.nc"},
            geos={"file": "toto.nc"},
        )

        level_1 = LevelComposite(
            level=1,
            probability="no",
            logical_op_list=[],
            aggregation_type="downStream",
            aggregation=aggregation,
            elements_event=[element1],
            localisation=localisation,
        )

        plain2 = {"threshold": 5, "comparison_op": "supegal", "units": "mm"}
        element2 = EventComposite(
            category="quantitative",
            field=field,
            plain=plain2,
            altitude={"filename": SETTINGS_DIR / "geos/altitudes/franxl1s100.nc"},
            geos={"file": "toto.nc"},
        )

        level_2 = LevelComposite(
            level=2,
            probability="no",
            logical_op_list=[],
            aggregation_type="downStream",
            aggregation=aggregation,
            elements_event=[element2],
            localisation=localisation,
        )

        plain3 = {"threshold": 15, "comparison_op": "supegal", "units": "mm"}
        element3 = EventComposite(
            category="quantitative",
            field=field,
            plain=plain3,
            altitude={"filename": SETTINGS_DIR / "geos/altitudes/franxl1s100.nc"},
            geos={"file": "toto.nc"},
        )

        level_3 = LevelComposite(
            level=3,
            probability="no",
            logical_op_list=[],
            aggregation_type="downStream",
            aggregation=aggregation,
            elements_event=[element3],
            localisation=localisation,
        )

        period = Period(
            id="751410a0-a404-45de-8548-1944af4c6e60",
            name="PROD+1h / PROD+24h",
            start="20191117T150000",
            stop="20191118T140000",
        )

        component = RiskComponentComposite(
            id="055f76ce-4f55-4c37-8284-2e0a165a88cb",
            name="pluie_for_test",
            production_id="afe389a0-145c-4836-8643-e2ad28b66dfc",
            production_name="Promethee_CD01",
            production_datetime="2019-11-17T14:00:00.000000",
            type="risk",
            levels=[level_1, level_2, level_3],
            hazard_id="abedd4b6-d857-4e44-b332-3c987f3a94c5",
            hazard_name="Pluies",
            period=period,
            product_comment=True,
        )

        component._risks_ds = risk_ds
        component._final_risk_da = final_risk_da

        reducer = Reducer(component=component)
        reducer.module = "unizone"
        level_max = max(risk_ds.risk_level.values)
        risk_max = max(final_risk_da.values)
        risk_min = min(final_risk_da.values)

        # on test la normalization du risque
        norm_risk = final_risk_da.values
        if level_max > 1:
            norm_risk = np.where(
                norm_risk, 1 - (((level_max - norm_risk) * 0.5) / (level_max - 1)), 0
            )
        assert (
            norm_risk
            == [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                1,
                1,
                1,
                0.5,
                0.5,
                0.5,
            ]
        ).all()

        # on teste la dtw : calul de distance et template
        reducer.compute_distance(norm_risk, method="first")
        reducer.reduction["risk_max"] = risk_max
        reducer.reduction["risk_min"] = risk_min
        reducer.reduction["level_maxi"] = level_max

        assert reducer.reduction["centroid"] == (
            0,
            0.75,
            1,
            0.75,
        )
        assert (
            reducer.reduction["template"]
            == "Zone en alerte à partir de {B1_start}. L’alerte est maximale "
            "{B2_period}. {B2_val}."
        )

        # on teste la reduction du risque
        reduced_risk, reducer.reduction = reducer.reduce_risk(
            component.final_risk_da, component.risks_ds
        )
        assert reduced_risk == [0, 1, 3, 1]
        for i in range(4):
            assert "B" + str(i) in reducer.reduction
        assert reducer.reduction["B2"]["EAU1__SOL"]["plain"]["min"] == 0.12
        assert reducer.reduction["B3"]["EAU1__SOL"]["plain"]["max"] == 16
        assert reducer.reduction["B1"]["EAU1__SOL"]["plain"]["units"] == "mm"
        assert "EAU1__SOL" not in reducer.reduction["B0"]

        # on teste les level_int level_max
        reducer.get_levels_val()
        assert reducer.reduction["level_int"]["EAU1__SOL"]["plain"]["min"] == 6.5
        assert reducer.reduction["level_max"]["EAU1__SOL"]["plain"]["value"] == 3.22

        # # on teste le builder
        builder = Monozone(reducer.reduction["template"])
        comment = builder.compute(reducer.reduction)
        assert comment == (
            "Zone en alerte à partir du milieu de nuit de dimanche à lundi. L’alerte "
            "est maximale lundi en matinée. Le cumul de pluie sur 1 heure atteint 3 à "
            "7 mm."
        )

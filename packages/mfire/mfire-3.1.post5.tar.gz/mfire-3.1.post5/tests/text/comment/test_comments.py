"""test_comments.py

Unit tests of the text.comment module.
"""
import numpy as np

# Third parties packages
import pytest

import mfire.utils.mfxarray as xr
from mfire.composite.components import RiskComponentComposite
from mfire.localisation.localisation_manager import Localisation

# Own package
from mfire.settings import Settings
from mfire.text.comment.multizone import ComponentHandlerLocalisation, new_multizone

COMPONENT_CONFIG = {
    "hazard_id": "hazard_metronome_precip",
    "period": {
        "id": "surveillance_period",
        "name": "De mardi 9h à mercredi midi",
        "start": "20201208T180000",
        "stop": "20201208T190000",
    },
    "geos": ["CD38_domain"],
    "hazard_name": "unknown",
    "levels": [
        {
            "level": 2,
            "probability": "no",
            "elements_event": [
                {
                    "field": {
                        "file": "PRECIP3__SOL.0014_0048_0001.netcdf",
                        "selection": {
                            "slice": {
                                "valid_time": ["20201208T210000", "20201208T230000"]
                            }
                        },
                        "grid_name": "grid name",
                        "name": "PRECIP3__SOL",
                    },
                    "plain": {"comparison_op": "sup", "threshold": 2.5, "units": "mm"},
                    "mountain": {"comparison_op": "sup", "threshold": 4, "units": "mm"},
                    "category": "quantitative",
                    "field_1": {
                        "file": "PRECIP1__SOL.0014_0048_0001.netcdf",
                        "selection": {
                            "slice": {
                                "valid_time": ["20201208T210000", "20201208T230000"]
                            }
                        },
                        "grid_name": "grid name",
                        "name": "PRECIP1__SOL",
                    },
                    "cum_period": 3,
                    "process": "Bertrand",
                    "mountain_altitude": 1000,
                    "altitude": {
                        "filename": Settings().altitudes_dirname / "franxl1s100.nc"
                    },
                    "geos": {"file": "toto.nc"},
                }
            ],
            "logical_op_list": [],
            "aggregation_type": "downStream",
            "aggregation": {"method": "requiredDensity", "kwargs": {"dr": 0.1}},
            "localisation": {
                "compass_split": True,
                "altitude_split": True,
            },
        },
        {
            "level": 3,
            "probability": "no",
            "elements_event": [
                {
                    "field": {
                        "file": "PRECIP3__SOL.0014_0048_0001.netcdf",
                        "selection": {
                            "slice": {
                                "valid_time": ["20201208T210000", "20201208T230000"]
                            }
                        },
                        "grid_name": "grid name",
                        "name": "PRECIP3__SOL",
                    },
                    "plain": {"comparison_op": "sup", "threshold": 3, "units": "mm"},
                    "mountain": {"comparison_op": "sup", "threshold": 5, "units": "mm"},
                    "category": "quantitative",
                    "field_1": {
                        "file": "PRECIP1__SOL.0014_0048_0001.netcdf",
                        "selection": {
                            "slice": {
                                "valid_time": ["20201208T210000", "20201208T230000"]
                            }
                        },
                        "grid_name": "grid name",
                        "name": "PRECIP3__SOL",
                    },
                    "cum_period": 3,
                    "process": "Bertrand",
                    "mountain_altitude": 1000,
                    "altitude": {
                        "filename": Settings().altitudes_dirname / "franxl1s100.nc"
                    },
                    "geos": {"file": "toto.nc"},
                }
            ],
            "logical_op_list": [],
            "aggregation_type": "downStream",
            "aggregation": {"method": "requiredDensity", "kwargs": {"dr": 0.1}},
            "localisation": {
                "compass_split": True,
                "altitude_split": True,
            },
        },
    ],
    "id": "cd38_risks",
    "type": "risk",
    "name": "Tableau de surveillance",
    "customer_id": "conseil_departemental_isere",
    "customerName": "unknown",
    "production_id": "UnknownProdId",
    "production_name": "UnknownProdName",
    "geos_descriptive": [],
    "product_comment": True,
    "alt_min": -100,
    "alt_max": 5000,
    "other_names": ["Précipitations abondantes"],
    "time_dimension": "valid_time",
    "production_datetime": "20201208T170000",
    "prod_id": 0,
    "config_hash": "2ad888dff17a87d0bb27ecdf99fe7e70",
    "mask_hash": "4ad72c6dcd07586f034413414f1c9ac6",
    "prod_hash": "7f71472b7c0c62ca74306736b83cd0a2",
}


MULTIZONE_TABLES = {
    "P1_0_1": {
        "localisation": {
            "name": "test",
            "data": np.array([[0, 1]]),
            "dims": ("period", "id"),
            "coords": {
                "period": ["20201208T18_to_20201208T19"],
                "id": ["CD38_Est", "CD38_NordOuest_+_c95e68d1"],
                "areaType": ("id", ["compass", "compass_+_"]),
                "areaName": ("id", ["Est", "NordOuest_+_SudOuest"]),
                "risk_level": 3,
            },
        },
        "config": {"production_datetime": "20201208T12"},
        "comment": "Risque prévu NordOuest_+_SudOuest ce mardi en soirée.",
    },
    "P3_0_5": {
        "localisation": {
            "name": "test",
            "data": np.array([[0, 1], [0, 0], [0, 1]]),
            "dims": ("period", "id"),
            "coords": {
                "period": [
                    "20190727T06_to_20190727T08",
                    "20190727T09_to_20190727T12",
                    "20190727T13_to_20190727T14",
                ],
                "id": ["13923f55", "bc6f2e89"],
                "areaType": ("id", ["", "Altitude"]),
                "areaName": ("id", ["Au dessus de 400m", "En dessous de 400m"]),
                "risk_level": 3,
            },
        },
        "config": {"production_datetime": "20190726T22"},
        "comment": (
            "Risque prévu samedi début de matinée et samedi en milieu de journée En "
            "dessous de 400m."
        ),
    },
    "P3_2_4_7": {
        "localisation": {
            "name": "test",
            "data": np.array([[0, 1, 1], [1, 0, 1], [0, 0, 1]]),
            "dims": ("period", "id"),
            "coords": {
                "period": [
                    "20190727T06_to_20190727T08",
                    "20190727T09_to_20190727T12",
                    "20190727T13_to_20190727T14",
                ],
                "id": ["13923f55", "bc6f2e89", "de3911ad"],
                "areaType": ("id", ["toto", "tata", "titi"]),
                "areaName": ("id", ["Toulouse", "Lyon", "Marseille Bébé"]),
                "risk_level": 3,
            },
        },
        "config": {"production_datetime": "20190726T22"},
        "comment": (
            "Risque prévu samedi en matinée et mi-journée Marseille Bébé, "
            "temporairement également Toulouse_+_Lyon."
        ),
    },
}


class TestMultiZone:
    """Class for testing multizone comment builder."""

    @pytest.mark.filterwarnings("ignore: warnings")
    def test_multizone(self):
        np.random.seed(42)

        """Method for testing multizone comment builder."""
        multizone = new_multizone("default")
        for _, loca_config in MULTIZONE_TABLES.items():
            COMPONENT_CONFIG.update(**loca_config["config"])

            loca_da = xr.DataArray(**loca_config["localisation"])
            loca_handler = Localisation.define_without_spatial(
                RiskComponentComposite(**COMPONENT_CONFIG), loca_da
            )

            compo = ComponentHandlerLocalisation(localisation_handler=loca_handler)
            multizone.compute(compo)

            assert multizone.text == loca_config["comment"]

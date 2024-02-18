from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFilter

import mfire.utils.mfxarray as xr
from mfire.composite import WeatherComposite
from mfire.settings import Settings
from mfire.sit_gen.segmentation import (
    BlobSegmentation,
    ContourSegmentation,
    get_segmentation,
)


class TestSegmentation:
    @staticmethod
    def get_ad_weather(dirname: Path):
        return {
            "id": "sitgen_ad",
            "condition": {
                "field": {
                    "file": dirname / "t2m.nc",
                    "selection": {
                        "sel": {},
                        "slice": {
                            "valid_time": [
                                "2022-06-08T00:00:00.000000",
                                "2022-06-09T00:00:00.000000",
                            ]
                        },
                        "isel": {},
                        "islice": {},
                    },
                    "grid_name": "globd025",
                    "name": "T__HAUTEUR2",
                },
                "category": "quantitative",
                "plain": {
                    "threshold": -40,
                    "comparison_op": "sup",
                    "units": "celsius",
                },
                "mountain": None,
                "mountain_altitude": None,
                "altitude": {
                    "filename": Settings().altitudes_dirname / "globd025.nc",
                    "grid_name": "globd025",
                    "alt_min": -100,
                    "alt_max": 10000,
                },
                "process": None,
                "geos": {
                    "file": dirname / "situation_generale_marine.nc",
                    "mask_id": ["global"],
                    "grid_name": "globd025",
                },
                "time_dimension": None,
                "aggregation": {
                    "kwargs": {
                        "dr": 0,
                        "central_weight": None,
                        "outer_weight": None,
                        "central_mask": None,
                    },
                    "method": "requiredDensity",
                },
                "aggregation_aval": None,
                "compute_list": [],
            },
            "params": {
                "msl": {
                    "file": dirname / "msl.nc",
                    "selection": {
                        "sel": {},
                        "slice": {
                            "valid_time": [
                                "2022-06-08T00:00:00.000000",
                                "2022-06-09T00:00:00.000000",
                            ]
                        },
                        "isel": {},
                        "islice": {},
                    },
                    "grid_name": "globd025",
                    "name": "P__MER",
                },
                "u_850": {
                    "file": dirname / "u_850.nc",
                    "selection": {
                        "sel": {},
                        "slice": {
                            "valid_time": [
                                "2022-06-08T00:00:00.000000",
                                "2022-06-09T00:00:00.000000",
                            ]
                        },
                        "isel": {},
                        "islice": {},
                    },
                    "grid_name": "globd025",
                    "name": "U__ISOBARE850",
                },
                "v_850": {
                    "file": dirname / "v_850.nc",
                    "selection": {
                        "sel": {},
                        "slice": {
                            "valid_time": [
                                "2022-06-08T00:00:00.000000",
                                "2022-06-09T00:00:00.000000",
                            ]
                        },
                        "isel": {},
                        "islice": {},
                    },
                    "grid_name": "globd025",
                    "name": "V__ISOBARE850",
                },
            },
            "units": {
                "msl": "hPa",
                "u_850": "km/h",
                "v_850": "km/h",
            },
            "altitude": None,
            "period": {
                "id": "751410a0-a404-45de-8548-1944af4c6e60",
                "name": "PROD+0h / PROD+24h",
                "start": "2022-06-08T00:00:00+00:00",
                "stop": "2022-06-09T00:00:00+00:00",
            },
            "geos": {
                "file": dirname / "situation_generale_marine.nc",
                "mask_id": ["global"],
                "grid_name": "globd025",
            },
            "localisation": {
                "compass_split": False,
                "altitude_split": False,
                "geos_descriptive": [],
            },
        }

    @staticmethod
    def get_front_weather(dirname: Path) -> dict:
        return {
            "id": "sitgen_fronts",
            "condition": {
                "field": {
                    "file": dirname / "t2m.nc",
                    "selection": {
                        "sel": {},
                        "slice": {
                            "valid_time": [
                                "2022-06-08T00:00:00.000000",
                                "2022-06-09T00:00:00.000000",
                            ]
                        },
                        "isel": {},
                        "islice": {},
                    },
                    "grid_name": "globd025",
                    "name": "T__HAUTEUR2",
                },
                "category": "quantitative",
                "plain": {
                    "threshold": -40,
                    "comparison_op": "sup",
                    "units": "celsius",
                },
                "mountain": None,
                "mountain_altitude": None,
                "altitude": {
                    "filename": Settings().altitudes_dirname / "globd025.nc",
                    "grid_name": "globd025",
                    "alt_min": -100,
                    "alt_max": 10000,
                },
                "process": None,
                "geos": {
                    "file": dirname / "situation_generale_marine.nc",
                    "mask_id": ["global"],
                    "grid_name": "globd025",
                },
                "time_dimension": None,
                "aggregation": {
                    "kwargs": {
                        "dr": 0,
                        "central_weight": None,
                        "outer_weight": None,
                        "central_mask": None,
                    },
                    "method": "requiredDensity",
                },
                "aggregation_aval": None,
                "compute_list": [],
            },
            "params": {
                "t2m": {
                    "file": dirname / "t2m.nc",
                    "selection": {
                        "sel": {},
                        "slice": {
                            "valid_time": [
                                "2022-06-08T00:00:00.000000",
                                "2022-06-09T00:00:00.000000",
                            ]
                        },
                        "isel": {},
                        "islice": {},
                    },
                    "grid_name": "globd025",
                    "name": "T__HAUTEUR2",
                },
                "r_700": {
                    "file": dirname / "r_700.nc",
                    "selection": {
                        "sel": {},
                        "slice": {
                            "valid_time": [
                                "2022-06-08T00:00:00.000000",
                                "2022-06-09T00:00:00.000000",
                            ]
                        },
                        "isel": {},
                        "islice": {},
                    },
                    "grid_name": "globd025",
                    "name": "HU__ISOBARE700",
                },
                "msl": {
                    "file": dirname / "msl.nc",
                    "selection": {
                        "sel": {},
                        "slice": {
                            "valid_time": [
                                "2022-06-08T00:00:00.000000",
                                "2022-06-09T00:00:00.000000",
                            ]
                        },
                        "isel": {},
                        "islice": {},
                    },
                    "grid_name": "globd025",
                    "name": "P__MER",
                },
                "u10": {
                    "file": dirname / "u10.nc",
                    "selection": {
                        "sel": {},
                        "slice": {
                            "valid_time": [
                                "2022-06-08T00:00:00.000000",
                                "2022-06-09T00:00:00.000000",
                            ]
                        },
                        "isel": {},
                        "islice": {},
                    },
                    "grid_name": "globd025",
                    "name": "U__HAUTEUR10",
                },
                "v10": {
                    "file": dirname / "v10.nc",
                    "selection": {
                        "sel": {},
                        "slice": {
                            "valid_time": [
                                "2022-06-08T00:00:00.000000",
                                "2022-06-09T00:00:00.000000",
                            ]
                        },
                        "isel": {},
                        "islice": {},
                    },
                    "grid_name": "globd025",
                    "name": "V__HAUTEUR10",
                },
                "wbpt_850": {
                    "file": dirname / "wbpt_850.nc",
                    "selection": {
                        "sel": {},
                        "slice": {
                            "valid_time": [
                                "2022-06-08T00:00:00.000000",
                                "2022-06-09T00:00:00.000000",
                            ]
                        },
                        "isel": {},
                        "islice": {},
                    },
                    "grid_name": "globd025",
                    "name": "THETAPW__ISOBARE850",
                },
            },
            "units": {
                "t2m": "°C",
                "r_700": "%",
                "msl": "hPa",
                "u10": "km/h",
                "v10": "km/h",
                "wbpt_850": "°C",
            },
            "altitude": None,
            "period": {
                "id": "751410a0-a404-45de-8548-1944af4c6e60",
                "name": "PROD+0h / PROD+24h",
                "start": "2022-06-08T00:00:00+00:00",
                "stop": "2022-06-09T00:00:00+00:00",
            },
            "geos": {
                "file": dirname / "situation_generale_marine.nc",
                "mask_id": ["global"],
                "grid_name": "globd025",
            },
            "localisation": {
                "compass_split": False,
                "altitude_split": False,
                "geos_descriptive": [],
            },
        }

    @staticmethod
    def create_ds(variables: dict):
        coords = dict(
            valid_time=[np.datetime64("2022-06-08T00:00:00.000000000")],
            latitude=np.arange(80, -0.25, -0.25),
            longitude=np.arange(-50, 60.25, 0.25),
        )
        dims = np.array([len(x) for x in coords.values()])
        das = {}
        for var, (geometry, shape) in variables.items():
            img = Image.new("L", tuple(dims[1:]))
            draw = ImageDraw.Draw(img)
            draw.__getattribute__(geometry)(shape, fill=200, width=3)
            arr = np.array(img.filter(ImageFilter.GaussianBlur(5))).T
            das[var] = xr.DataArray([arr], coords=coords, dims=coords) / arr.max() * 0.8
        return xr.Dataset(das)

    @pytest.mark.skip(reason="for now, the marine par is not used")
    def test_contour_segmentation(self, working_dir: Path):
        weather = WeatherComposite(**self.get_front_weather(working_dir / "data"))
        segmentation = get_segmentation(weather)
        assert isinstance(segmentation, ContourSegmentation)
        front_ds = self.create_ds(
            {
                "front quasi-stationnaire": ("line", [(160, 220), (240, 330)]),
                "front froid": ("line", [(160, 220), (240, 110)]),
                "front occlus": ("line", [(160, 220), (80, 330)]),
                "front chaud": ("line", [(160, 220), (80, 110)]),
            }
        )
        result = segmentation.process(front_ds)

        # on trouvé 4 fronts
        assert len(result["2022-06-08T00:00:00.000000000"]["features"]) == 4

    def test_blob_segmentation(self, working_dir: Path):
        weather = WeatherComposite(**self.get_ad_weather(working_dir / "data"))
        segmentation = get_segmentation(weather)
        assert isinstance(segmentation, BlobSegmentation)
        ad_ds = self.create_ds(
            {
                "anticyclone": ("ellipse", (40, 55, 60, 80)),
                "depression": ("ellipse", (200, 275, 220, 300)),
            }
        )
        result = segmentation.process(ad_ds)

        # on a trouvé 1 depression et 1 anticyclone
        assert len(result["2022-06-08T00:00:00.000000000"]["features"]) == 2

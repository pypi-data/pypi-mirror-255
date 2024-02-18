import pytest

import mfire.utils.mfxarray as xr
from mfire.mask.fusion import FusionZone, extract_area_name


class TestFusionZone:
    @pytest.mark.parametrize(
        "area_da,expected",
        [
            (
                [
                    [[True, False]],
                    [[True, False]],
                ],
                False,
            ),
            (
                [
                    [[True, False]],
                    [[False, True]],
                ],
                True,
            ),
        ],
    )
    def test_check_union_differs(self, area_da, expected):
        ids_list = ["axe", "zone1", "zone2"]
        lon, lat = [5, 6], [1]

        mask_ds = xr.Dataset(
            {
                "franxl1s100": (
                    ["id", "latitude_franxl1s100", "longitude_franxl1s100"],
                    [[[True, True]]] + area_da,
                )
            },
            coords={
                "id": ids_list,
                "latitude_franxl1s100": lat,
                "longitude_franxl1s100": lon,
            },
        )

        fz = FusionZone(mask_ds, axe_id="axe")
        assert fz.check_union_differs("zone1", "zone2") == expected

    @pytest.mark.parametrize(
        "area_da,expected",
        [
            (
                [
                    [[True, False]],
                    [[True, False]],
                ],
                False,
            ),
            (
                [
                    [[True, False]],
                    [[False, True]],
                ],
                True,
            ),
        ],
    )
    def test_check_zones_differ(self, area_da, expected):
        ids_list = ["axe", "zone1", "zone2"]
        lon, lat = [5, 6], [1]

        mask_ds = xr.Dataset(
            {
                "franxl1s100": (
                    ["id", "latitude_franxl1s100", "longitude_franxl1s100"],
                    [[[True, True]]] + area_da,
                )
            },
            coords={
                "id": ids_list,
                "latitude_franxl1s100": lat,
                "longitude_franxl1s100": lon,
            },
        )

        fz = FusionZone(mask_ds, axe_id="axe")
        assert fz.check_zones_differ("zone1", "zone2") == expected

    def test_compute(self):
        ids_list = ["axe", "zone1", "zone2", "zone3"]
        lon, lat = [5, 6, 7], [1]

        mask_ds = xr.Dataset(
            {
                "franxl1s100": (
                    ["id", "latitude_franxl1s100", "longitude_franxl1s100"],
                    [
                        [[True, True, True]],
                        [[False, False, True]],
                        [[True, False, False]],
                        [[False, True, False]],
                    ],
                )
            },
            coords={
                "id": ids_list,
                "latitude_franxl1s100": lat,
                "longitude_franxl1s100": lon,
                "areaName": (
                    ["id"],
                    ["area_axe", "area_name_1", "area_name_2", "area_name_3"],
                ),
            },
        )

        fz = FusionZone(mask_ds, axe_id="axe")
        assert fz.compute() == [
            {
                "name": "area_name_1 et area_name_2",
                "base": ["zone1", "zone2"],
                "id": "axe__zone1__zone2",
                "areaType": "fusion2",
            },
            {
                "name": "area_name_1 et area_name_3",
                "base": ["zone1", "zone3"],
                "id": "axe__zone1__zone3",
                "areaType": "fusion2",
            },
            {
                "name": "area_name_2 et area_name_3",
                "base": ["zone2", "zone3"],
                "id": "axe__zone2__zone3",
                "areaType": "fusion2",
            },
        ]


class TestFusionZoneFunctions:
    def test_extract_area_name(self):
        assert extract_area_name({"name": "nom"}) == "nom"
        assert extract_area_name({"label": "nom"}) == "nom"
        assert extract_area_name({"alt_label": "nom"}) == "nom"
        assert extract_area_name({"areaName": "nom"}) == "nom"
        assert extract_area_name({"area_name": "nom"}) == "nom"

        with pytest.raises(ValueError):
            _ = extract_area_name({"notknownkey": "nom"})

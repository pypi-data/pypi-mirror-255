import numpy as np
import pytest

import mfire.utils.mfxarray as xr
from mfire.composite.fields import FieldComposite, Selection
from mfire.utils.date import Datetime
from tests.composite.factories import FieldCompositeFactory
from tests.functions_test import assert_identically_close


class TestFieldComposite:
    def test_check_selection(self):
        field_compo = FieldCompositeFactory()
        assert field_compo.selection == Selection()

    @pytest.mark.parametrize("test_file_path", [{"extension": "nc"}], indirect=True)
    def test_compute(self, test_file_path):
        da = xr.DataArray(
            [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
            coords={"A": [1, 2, 3], "B": [4, 5]},
            name="field_name",
        )
        da.to_netcdf(test_file_path)

        selection = Selection(sel={"B": 5}, slice={"A": slice(2, 3)})
        field_compo = FieldCompositeFactory(
            file=test_file_path,
            selection=selection,
        )
        assert_identically_close(
            field_compo.compute(),
            xr.DataArray(
                [4.0, 6.0], coords={"A": [2, 3], "B": 5}, dims=["A"], name="field_name"
            ),
        )

        selection = Selection(isel={"B": 0}, islice={"A": slice(0, 2)})
        field_compo = FieldCompositeFactory(
            file=test_file_path,
            selection=selection,
        )
        assert_identically_close(
            field_compo.compute(),
            xr.DataArray(
                [1.0, 3.0], coords={"A": [1, 2], "B": 4}, dims=["A"], name="field_name"
            ),
        )

    @pytest.mark.parametrize(
        "test_file_path", [{"nbr": 2, "extension": "nc"}], indirect=True
    )
    def test_compute_with_list(self, test_file_path):
        da = xr.DataArray(
            [[[1.0, 2.0, 3.0, 4.0, 5.0], [6.0, 7.0, 8.0, 9.0, 10.0]]],
            coords={
                "valid_time": [Datetime(2023, 3, 1).as_np_dt64],
                "latitude": [41.02, 41.03],
                "longitude": [10.40, 10.41, 10.42, 10.43, 10.44],
            },
            name="field_name_1",
            attrs={"units": "cm"},
        )
        da.to_netcdf(test_file_path[0])

        da = xr.DataArray(
            [[[110, 120, 130], [140, 150, 160]]],
            coords={
                "valid_time": [Datetime(2023, 3, 2).as_np_dt64],
                "latitude": [41.02, 41.03],
                "longitude": [10.40, 10.42, 10.44],
            },
            name="field_name_2",
            attrs={"units": "mm"},
        )
        da.to_netcdf(test_file_path[1])

        field_compo = FieldCompositeFactory(
            file=test_file_path,
            grid_name="franxl1s100",
        )

        result = field_compo.compute()
        expected = xr.DataArray(
            [
                [
                    [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
                    [1.0, 2.0, 3.0, 4.0, 5.0, np.nan],
                    [6.0, 7.0, 8.0, 9.0, 10.0, np.nan],
                ],
                [
                    [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
                    [11.0, 11.0, 12.0, 12.0, 13.0, np.nan],
                    [14.0, 14.0, 15.0, 15.0, 16.0, np.nan],
                ],
            ],
            coords={
                "valid_time": [Datetime(2023, 3, i).as_np_dt64 for i in range(1, 3)],
                "latitude": [41.01, 41.02, 41.03],
                "longitude": [10.40, 10.41, 10.42, 10.43, 10.44, 10.45],
            },
            name="field_name_1",
            attrs={"units": "cm"},
        )
        assert_identically_close(
            result,
            expected,
        )

    @pytest.mark.parametrize(
        "test_file_path", [{"nbr": 2, "extension": "nc"}], indirect=True
    )
    def test_compute_with_list_and_wwmf(self, test_file_path):
        da = xr.DataArray(
            [[[1, 4, 11, 14, 17], [19, 20, 25, 29, 16]]],
            coords={
                "valid_time": [Datetime(2023, 3, 1).as_np_dt64],
                "latitude": [41.02, 41.03],
                "longitude": [10.40, 10.41, 10.42, 10.43, 10.44],
            },
            name="field_name_1",
            attrs={"units": "w1"},
        )
        da.to_netcdf(test_file_path[0])

        da = xr.DataArray(
            [[[62, 59, 51], [31, 40, 92]]],
            coords={
                "valid_time": [Datetime(2023, 3, 2).as_np_dt64],
                "latitude": [41.02, 41.03],
                "longitude": [10.40, 10.42, 10.44],
            },
            name="field_name_2",
            attrs={"units": "wwmf"},
        )
        da.to_netcdf(test_file_path[1])

        field_compo = FieldCompositeFactory(
            file=test_file_path,
            grid_name="franxl1s100",
        )

        result = field_compo.compute()
        expected = xr.DataArray(
            [
                [
                    [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
                    [31, 38, 53, 58, 63, np.nan],
                    [70, 77, 93, 98, 62, np.nan],
                ],
                [
                    [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
                    [62, 62, 59, 59, 51, np.nan],
                    [31, 31, 40, 40, 92, np.nan],
                ],
            ],
            coords={
                "valid_time": [Datetime(2023, 3, i).as_np_dt64 for i in range(1, 3)],
                "latitude": [41.01, 41.02, 41.03],
                "longitude": [10.40, 10.41, 10.42, 10.43, 10.44, 10.45],
            },
            name="field_name_1",
            attrs={"units": "wwmf"},
        )
        assert_identically_close(
            result,
            expected,
        )

    @pytest.mark.parametrize("test_file_path", [{"extension": "nc"}], indirect=True)
    def test_get_coord(self, test_file_path):
        da = xr.DataArray(
            [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
            coords={"A": [1, 2, 3], "B": [4, 5]},
            name="field_name",
        )
        da.to_netcdf(test_file_path)
        field_compo = FieldComposite(
            file=test_file_path, grid_name="grid_name", name="name"
        )
        assert_identically_close(
            field_compo.get_coord("A"),
            xr.DataArray([1.0, 2.0, 3.0], coords={"A": [1, 2, 3]}, name="A"),
        )

import numpy as np
import pytest

import mfire.utils.mfxarray as xr
from mfire.localisation.table import SummarizedTable
from mfire.utils.date import Datetime, Period
from tests.functions_test import assert_identically_close


class TestTable:
    def test__squeeze_empty_period(self):
        periods = [
            "20190727T06_to_20190727T09",
            "20190727T10_to_20190727T13",
            "20190727T14_to_20190727T17",
        ]
        request_time = Datetime("20190727T06")
        full_period = Period(Datetime("20190727T06"), Datetime("20190727T17"))
        da = xr.DataArray(
            [[0.0, 1.0, 0.0]], coords={"id": ["id_1"], "period": periods}, name="da"
        )

        table = SummarizedTable(da, request_time, full_period)

        expected_working_table = xr.DataArray(
            [[1.0]],
            coords={
                "id": ["id_1"],
                "period": ["20190727T10_to_20190727T13"],
                "raw": (["id"], [1]),
            },
            dims=["id", "period"],
            name="da",
        )
        assert_identically_close(table.working_table, expected_working_table)

        assert table.raw_table == ["1", 1]

    def test__merge_similar_period(self):
        periods = [
            "20190727T06_to_20190727T09",
            "20190727T10_to_20190727T13",
            "20190727T14_to_20190727T17",
        ]
        request_time = Datetime("20190727T06")
        full_period = Period(Datetime("20190727T06"), Datetime("20190727T17"))
        da = xr.DataArray(
            [[1.0, 1.0, 2.0]], coords={"id": ["id_1"], "period": periods}, name="da"
        )

        table = SummarizedTable(da, request_time, full_period)
        expected_working_table = xr.DataArray(
            [[1.0, 2.0]],
            coords={
                "id": ["id_1"],
                "period": [
                    "20190727T06_to_20190727T09_+_20190727T10_to_20190727T13",
                    "20190727T14_to_20190727T17",
                ],
                "raw": (["id"], [4]),
            },
            dims=["id", "period"],
            name="da",
        )
        assert_identically_close(table.working_table, expected_working_table)

        assert table.raw_table == ["2", 4]

    def test__merge_period_with_same_name(self):
        np.random.seed(42)

        # Without error
        periods = [
            "20190727T06_to_20190727T09",
            "20190727T07_to_20190727T10",
            "20190727T14_to_20190727T17",
        ]
        request_time = Datetime("20190727T06")
        full_period = Period(Datetime("20190727T06"), Datetime("20190727T17"))
        da = xr.DataArray(
            [[1.0, 2.0, 3.0]], coords={"id": ["id_1"], "period": periods}, name="da"
        )

        table = SummarizedTable(da, request_time, full_period)
        np.testing.assert_equal(table.working_table.values.flatten(), [2.0, 3.0])

        assert table.raw_table == ["2", 7]

        # With error in the date
        periods = [
            "20190727T06_to_20190727T09",
            "20190727T07_to_20190727T10",
            "20190727T14_to_truc",
        ]
        da = xr.DataArray(
            [[1.0, 2.0, 3.0]], coords={"id": ["id_1"], "period": periods}, name="da"
        )

        table = SummarizedTable(da, request_time, full_period)
        np.testing.assert_equal(table.working_table.values.flatten(), [1.0, 2.0, 3.0])

        assert table.raw_table == ["3", 11]

    @pytest.mark.filterwarnings("ignore: invalid value")
    def test_summarized_table(self):

        full_period = Period("20190726T16", "20190727T15")
        request_time = Datetime("20190726T16")
        df = xr.Dataset()
        df.coords["period"] = [
            "20190727T06_to_20190727T09",
            "20190727T10_to_20190727T13",
            "20190727T14_to_20190727T17",
        ]
        df.coords["id"] = [f"zone{k+1}" for k in range(3)]
        df["elt"] = (("id", "period"), [[0, 1, 1], [0, 1, 1], [1, 0, 1]])

        table_handler = SummarizedTable(
            df["elt"], request_time=request_time, full_period=full_period
        )

        dout = xr.Dataset()
        dout.coords["period"] = [
            "20190727T06_to_20190727T09",
            "20190727T10_to_20190727T13",
            "20190727T14_to_20190727T17",
        ]
        dout.coords["id"] = ["zone1_+_zone2", "zone3"]
        dout["elt"] = (("id", "period"), [[0.0, 1.0, 1.0], [1.0, 0.0, 1.0]])
        assert table_handler.unique_name == "P3_3_5"
        assert_identically_close(table_handler.unique_table, dout["elt"])

        df = xr.Dataset()
        df.coords["period"] = [
            "20190727T06_to_20190727T09",
            "20190727T10_to_20190727T13",
            "20190727T14_to_20190727T17",
        ]
        df.coords["id"] = [f"zone{k+1}" for k in range(3)]
        df["elt"] = (("id", "period"), [[1, 0, 0], [0, 1, 1], [1, 0, 0]])

        dout = xr.Dataset()
        dout.coords["id"] = ["zone2", "zone1_+_zone3"]
        dout.coords["period"] = [
            "20190727T06_to_20190727T09",
            "20190727T10_to_20190727T13_+_20190727T14_to_20190727T17",
        ]
        dout["elt"] = (("id", "period"), [[0.0, 1.0], [1.0, 0.0]])
        table_handler = SummarizedTable(
            df["elt"], request_time=request_time, full_period=full_period
        )
        assert table_handler.unique_name == "P2_1_2"
        assert_identically_close(table_handler.unique_table, dout["elt"])

    def test_merge_period_due_to_name(self):
        full_period = Period("20190726T16", "20190727T15")
        request_time = Datetime("20190726T16")
        df = xr.Dataset()
        df.coords["period"] = [
            "20190727T06_to_20190727T11",
            "20190727T14_to_20190727T15",
            "20190727T15_to_20190727T16",
        ]
        df.coords["id"] = [f"zone{k+1}" for k in range(3)]
        df["elt"] = (("id", "period"), [[0, 1, 1], [0, 1, 1], [1, 0, 1]])

        table_handler = SummarizedTable(
            df["elt"], request_time=request_time, full_period=full_period
        )

        dout = xr.Dataset()
        dout.coords["period"] = [
            "20190727T06_to_20190727T11",
            "20190727T14_to_20190727T16",
        ]
        dout.coords["id"] = ["zone1_+_zone2", "zone3"]
        dout["elt"] = (("id", "period"), [[0.0, 1.0], [1.0, 1.0]])

        assert_identically_close(table_handler.unique_table, dout["elt"])
        assert table_handler.unique_name == "P2_1_3"

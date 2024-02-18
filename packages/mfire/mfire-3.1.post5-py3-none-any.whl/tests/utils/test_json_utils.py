from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

from mfire.utils import JsonFile
from tests.composite.factories import PeriodFactory


class TestJsonFile:
    @pytest.mark.parametrize(
        "test_file",
        [{"content": '{"a":1, "b":2}', "extension": "json"}],
        indirect=True,
    )
    def test_load(self, test_file):
        json = JsonFile(open(test_file.name, "r"))
        assert json.load() == {"a": 1, "b": 2}

        json = JsonFile(test_file.name)
        assert json.load() == {"a": 1, "b": 2}

    @pytest.mark.parametrize(
        "test_file_path",
        [{"extension": "json"}],
        indirect=True,
    )
    def test_dump_with_filename(self, test_file_path, assert_equals_result):
        content = {
            "a": PeriodFactory(),
            "b": datetime(2023, 3, 1),
            "c": slice(2, 4, 1),
            "d": np.ndarray((1,), buffer=np.array([1])),
            "e": Path("test"),
        }
        json = JsonFile(test_file_path)
        json.dump(content)

        result = test_file_path.read_text()
        assert_equals_result(result)

        # Try with a non-Json serializable object
        content = {"a": self}
        with pytest.raises(
            TypeError, match="Object of type TestJsonFile is not JSON serializable"
        ):
            json.dump(content)

    @pytest.mark.parametrize(
        "test_file_path",
        [{"extension": "json"}],
        indirect=True,
    )
    def test_dump_with_file(self, test_file_path, assert_equals_result):
        content = {
            "a": PeriodFactory(),
            "b": datetime(2023, 3, 1),
            "c": slice(2, 4, 1),
            "d": np.ndarray((1,), buffer=np.array([1])),
            "e": Path("test"),
        }
        f = open(test_file_path, "w")
        json = JsonFile(f)
        json.dump(content)
        f.close()

        result = test_file_path.read_text()
        assert_equals_result(result)

        # Try with a non-Json serializable object
        content = {"a": self}
        with pytest.raises(
            TypeError, match="Object of type TestJsonFile is not JSON serializable"
        ):
            json.dump(content)

    @pytest.mark.parametrize(
        "test_file_path", [{"nbr": 3, "extension": "json"}], indirect=True
    )
    def test_is_equal_to(self, test_file_path):
        json1 = JsonFile(test_file_path[0])
        json2 = JsonFile(test_file_path[1])

        json1.dump({"a": 1, "b": 2})
        json2.dump({"b": 2, "a": 1})
        assert json1 == json2

        json3 = JsonFile(test_file_path[2])
        json3.dump({"a": 1, "b": 3})
        assert json1 != json3

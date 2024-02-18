import json
from pathlib import Path
from typing import Any, Callable

from mfire.settings import MONOZONE, SIT_GEN, TEMPLATES_FILENAMES
from mfire.text.template import read_template


class TestConstants:
    def _parse_json(self, filename: Path):
        try:
            with open(filename) as f:
                return json.load(f)
        except ValueError:
            return None

    def _check(self, val: Any, read_func: Callable):
        if isinstance(val, Path):
            assert val.is_file(), f"File {val} does not exist"
            assert read_func(val) is not None, f"File {val} can't be read"
        elif isinstance(val, dict):
            for val in val.values():
                self._check(val, read_func=read_func)

    def test_templates_filenames(self):
        self._check(TEMPLATES_FILENAMES, read_func=read_template)

    def test_monozone(self):
        self._check(MONOZONE, read_func=read_template)

    def test_sit_gen(self):
        self._check(SIT_GEN, read_func=self._parse_json)

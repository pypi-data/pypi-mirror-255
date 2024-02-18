from pathlib import Path

import pytest

from mfire.text.sit_gen.builders import SitGenBuilder
from mfire.utils import JsonFile


class TestSitGenBuilder:

    inputs_dir: Path = Path(__file__).parent / "inputs"

    @pytest.mark.parametrize(
        "key",
        [
            "large_mediterranee",
            "grand_large_smdsm",
            "large_atlantique_navtex_ism",
            "cote_manche_atlantique",
        ],
    )
    def test_compute(self, key, assert_equals_result):
        builder = SitGenBuilder()
        reduction = JsonFile(self.inputs_dir / "reduction.json").load()
        builder.compute(reduction[key])
        assert_equals_result(builder._text)

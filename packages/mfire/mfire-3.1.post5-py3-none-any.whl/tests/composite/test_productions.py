from pathlib import Path

import pytest

import mfire.utils.mfxarray as xr
from mfire.composite import ProductionComposite
from mfire.settings import SETTINGS_DIR
from mfire.utils import JsonFile, recursive_format
from tests.composite.factories import (
    ProductionCompositeFactory,
    RiskComponentCompositeFactory,
    TextComponentCompositeFactory,
)
from tests.functions_test import assert_identically_close


class TestProductionComposite:

    inputs_dir: Path = Path(__file__).parent / "inputs"

    def test_compute(self):
        production = ProductionCompositeFactory(
            components=[
                TextComponentCompositeFactory(),
                RiskComponentCompositeFactory(),
            ]
        )
        production.compute()

        assert len(production.components) == 2
        assert_identically_close(xr.Dataset(), production.components[0].weathers_ds)
        assert_identically_close(xr.Dataset(), production.components[1].risks_ds)

    @pytest.mark.parametrize("config", ["small_conf_text.json", "small_conf_risk.json"])
    def test_integration(self, root_path_cwd, config, assert_equals_result):
        # We need to CWD in root since we load an altitude field
        data = JsonFile(self.inputs_dir / config).load()
        data_prod = next(iter(data.values()))
        prod = ProductionComposite(
            **recursive_format(data_prod, values={"settings_dir": SETTINGS_DIR})
        )

        assert_equals_result(prod)

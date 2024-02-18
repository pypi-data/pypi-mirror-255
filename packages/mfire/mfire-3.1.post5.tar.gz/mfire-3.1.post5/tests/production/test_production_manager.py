import shutil
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from mfire.production.production_manager import ProductionManager
from mfire.utils import JsonFile
from mfire.utils.date import Datetime


class TestProductionManager:
    inputs_dir: Path = Path(__file__).parent / "inputs"

    def _copy_files(self, path: Path):
        for filename in ["small_conf.json", "altitude.nc", "field.nc", "mask.nc"]:
            shutil.copy(self.inputs_dir / filename, path / filename)

    @patch("mfire.utils.date.Datetime.now")
    def test_compute_single(self, mock_date, tmp_path_cwd, assert_equals_result):
        np.random.seed(42)
        mock_date.return_value = Datetime(2023, 3, 1)
        self._copy_files(tmp_path_cwd)
        manager = ProductionManager.load(filename=tmp_path_cwd / "small_conf.json")

        result = manager.compute_single(manager.components[0])
        assert_equals_result(result)

    @pytest.fixture(scope="session")
    def test_compute(
        self,
        tmp_path_cwd,
        assert_equals_result,
    ):
        self._copy_files(tmp_path_cwd)
        manager = ProductionManager.load(filename=tmp_path_cwd / "small_conf.json")
        manager.compute(nproc=1)

        # On récupère le fichier produit
        output_dir = pytest.TempPathFactory.mktemp("working_dir")
        output_filename = next(
            f for f in output_dir.iterdir() if f.name.startswith("prom_Test_config")
        )

        data = JsonFile(output_filename).load()

        # On pop ce qui retourne l'heure à laquelle PROMETHEE a ete produit.
        data.pop("DateProduction")

        # On va enlever les commentaires detailles (c'est pas le but du module de
        # tester qu'ils sont correct)
        data["Components"]["Aleas"][0].pop("DetailComment")
        data["Components"]["Aleas"][1].pop("DetailComment")

        assert_equals_result(data)

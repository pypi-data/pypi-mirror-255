import os
from pathlib import Path
from shutil import copytree

import pytest

import mfire.utils.mfxarray as xr
from mfire.tasks.preprocess_data import DataPreprocessor
from tests.functions_test import assert_identically_close


class TestDataPreprocess:
    # inputs directory tree needed :
    # configuration
    config_basename = "configs/data_task_config.json"
    # grib files in  source_data_dir = "data/20210212T0000/sympo/FRANXL1S100/"
    # resulting netcdf file
    preproc_exp_dir = "expected_data/20210212T0000/promethee/FRANXL1S100/"

    def get_config_filename(self, dirname: Path) -> Path:
        """Return the data task config file's name

        Args:
            dirname (str): Current wotrking directory's path

        Returns:
            str: Data task config file's name
        """
        return Path(dirname) / self.config_basename

    @pytest.fixture(scope="session")
    def local_working_dir(self, working_dir: Path) -> Path:
        """working_dir : pytest fixture for creating a new
        tmp working directory
        """

        inputs_dir: Path = Path(__file__).parent / "inputs/test_preprocess_data/"
        copytree(inputs_dir, working_dir, dirs_exist_ok=True)
        return working_dir

    def stacks_preprocessor(self, dirname: Path):
        """dirname : pytest fixture for creating a new
        tmp working directory
        """
        preprocessor = DataPreprocessor(
            self.get_config_filename(dirname), "psym_archive"
        )
        stacks = preprocessor.build_stack()

        return stacks

    def test_build_stack(self, local_working_dir: Path):
        """teste le build_stack :
        Builds a kind of "task processing stack"

        """
        stack = self.stacks_preprocessor(local_working_dir)

        stacks_dict_key_filename = ["grib_filename", "preproc_filename"]
        stacks_dict_key_dict = [
            "backend_kwargs",
            "grib_attrs",
            "postproc",
            "preproc_attrs",
        ]

        stacks_dict_key = stacks_dict_key_filename + stacks_dict_key_dict

        grib_attrs_keys = ["PROMETHEE_z_ref", "units"]
        postproc_dict_keys = ["start", "stop", "step", "param", "accum"]
        preproc_attrs_keys = ["source_grid", "preproc_grid", "source_step"]

        for file_conf in stack:
            assert set(file_conf) == set(stacks_dict_key)
            for key, val in file_conf.items():
                list_k_grib_attrs = [v for v in val if key == "grib_attrs"]
                if list_k_grib_attrs:
                    assert set(list_k_grib_attrs) == set(grib_attrs_keys)

                list_k_postproc_dict = [v for v in val if key == "postproc_dict"]
                if list_k_postproc_dict:
                    assert set(list_k_postproc_dict) == set(postproc_dict_keys)

                list_k_preproc_attrs = [v for v in val if key == "preproc_attrs"]
                if list_k_preproc_attrs:
                    assert set(list_k_preproc_attrs) == set(preproc_attrs_keys)

    def test_get_backend_kwargs(self, local_working_dir: Path):
        """teste get_backend_kwargs"""
        backend_kwargs_keys = ["read_keys", "filter_by_keys", "indexpath"]
        stack = self.stacks_preprocessor(local_working_dir)

        read_keys = [
            "discipline",
            "parameterCategory",
            "productDefinitionTemplateNumber",
            "parameterNumber",
            "typeOfFirstFixedSurface",
            "level",
            "typeOfStatisticalProcessing",
            "lengthOfTimeRange",
            "units",
            "name",
            "units",
            "startStep",
            "endStep",
            "stepRange",
        ]

        filter_by_keys = [
            "discipline",
            "parameterCategory",
            "productDefinitionTemplateNumber",
            "parameterNumber",
            "typeOfFirstFixedSurface",
            "level",
            "typeOfStatisticalProcessing",
            "lengthOfTimeRange",
            "indexpath",
        ]

        for file_conf in stack:
            for key, val in file_conf.items():
                if key == "backend_kwargs":
                    list_backend_kwargs = [v for v in val]

                    assert set(list_backend_kwargs) == set(backend_kwargs_keys)

                    for read in val["read_keys"]:
                        assert read in read_keys

                    for fil in val["filter_by_keys"]:
                        assert fil in filter_by_keys

    def test_preproc_filename(self, local_working_dir: Path):
        """teste la réalisation des fichiers netcdft"""

        os.chdir(local_working_dir)

        preprocessor = DataPreprocessor(
            self.get_config_filename(local_working_dir), "psym_archive"
        )

        preprocessor.preprocess(nproc=1)
        stack = preprocessor.build_stack()
        preproc_filename = []
        for file_conf in stack:
            for key, val in file_conf.items():
                if key == "preproc_filename":
                    preproc_filename.append(val)

        preproc_filename_set = set(preproc_filename)

        for filename in preproc_filename_set:
            filename = Path(filename)
            assert filename.exists()
            # comparing dataarrays with the expected ones
            exp_filename = local_working_dir / self.preproc_exp_dir / filename.name
            preproc_da = xr.open_dataarray(filename)
            print("file", filename)
            exp_da = xr.open_dataarray(exp_filename)
            print("exp", exp_filename)
            assert_identically_close(preproc_da, exp_da)

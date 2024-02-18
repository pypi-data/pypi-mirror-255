import filecmp
import logging
import os
import shutil
import sys
from difflib import unified_diff
from pathlib import Path
from typing import Any, List, Union

import numpy as np
import pytest

import mfire.utils.mfxarray as xr
from mfire.settings import Settings
from mfire.utils import JsonFile
from tests.functions_test import assert_identically_close

logging.getLogger("faker").setLevel(logging.ERROR)


@pytest.fixture(autouse=True)
def test_cleanup():
    yield
    shutil.rmtree(Settings().cache_dirname, ignore_errors=True)


def create_nc_field_SG(name: str, vmin: float, vmax: float, units: str):
    coords = dict(
        valid_time=[np.datetime64("2022-06-08T00:00:00.000000000")],
        latitude=np.arange(90, -90.25, -0.25),
        longitude=np.arange(-180, 180, 0.25),
    )
    dims = tuple([len(v) for v in coords.values()])
    arr = np.random.randint(vmin, vmax, dims)
    da = (vmax - vmin) * xr.DataArray(arr, coords=coords, dims=coords, name=name) + vmin
    da.attrs["units"] = units
    return da


@pytest.fixture(scope="session")
def working_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    working_dir = tmp_path_factory.mktemp("working_dir")
    Settings().set_full_working_dir(working_dir=working_dir)

    data_dir = Settings().data_dirname
    data_dir.mkdir(parents=True, exist_ok=True)

    # Settings SG files
    sg_fields = (
        ("r_700", 0, 100, "%"),
        ("msl", 94036, 105782, "hPa"),
        ("t2m", 194, 323, "K"),
        ("wbpt_850", 232, 302, "K"),
        ("u10", -25, 31, "m/s"),
        ("v10", -28, 26, "m/s"),
        ("u_850", -48, 45, "m/s"),
        ("v_850", -50, 35, "m/s"),
    )

    for field in sg_fields:
        create_nc_field_SG(*field).to_netcdf(data_dir / f"{field[0]}.nc")

    # Setting SG mask
    coords = dict(
        latitude=np.arange(80, -0.25, -0.25),
        longitude=np.arange(-50, 60.25, 0.25),
        id=["global"],
    )
    xr.DataArray(
        np.ones([len(v) for v in coords.values()]),
        coords=coords,
        dims=tuple(coords),
        name="globd025",
    ).to_netcdf(data_dir / "situation_generale_marine.nc")

    return working_dir


@pytest.fixture()
def tmp_path_cwd(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def root_path(request):
    return request.config.rootdir


@pytest.fixture()
def root_path_cwd(monkeypatch, request):
    monkeypatch.chdir(request.config.rootdir)
    return request.config.rootdir


@pytest.fixture()
def test_path(request) -> Path:
    return Path(request.config.rootdir) / "tests"


@pytest.fixture()
def test_file_path(request, tmp_path) -> Union[Path, List[Path]]:
    info = getattr(request, "param", {})
    extension = info.get("extension", "txt")
    nbr = info.get("nbr", 1)
    filename = info.get("name", "file")
    if nbr > 1:
        files = [tmp_path / f"{filename}_{i}.{extension}" for i in range(nbr)]
    else:
        files = [tmp_path / f"{filename}.{extension}"]

    for f in files:
        f.unlink(missing_ok=True)

    if nbr > 1:
        yield files
    else:
        yield files[0]

    for f in files:
        f.unlink(missing_ok=True)


@pytest.fixture()
def test_file(request, tmp_path):
    info = getattr(request, "param", {})
    extension = info.get("extension", "txt")
    path = tmp_path / f"file.{extension}"
    path.unlink(missing_ok=True)

    f = open(path, "w")
    if (content := info.get("content")) is not None:
        f.write(content)
    f.close()

    yield open(path, "r")
    path.unlink(missing_ok=True)


def _assert_equals_result(ref_path: Path, output_path: Path, data: Any):
    output_json = JsonFile(output_path)
    ref_json = JsonFile(ref_path)
    if not ref_path.exists():
        ref_json.dump(data, indent=2)
    else:
        output_json.dump(data, indent=2)

        if not ref_json.is_equal_to(output_json):
            os.system(f"meld {ref_path} {output_path}")

            if not ref_json.is_equal_to(output_json):
                diff_lines = unified_diff(
                    str(ref_json.load()),
                    str(output_json.load()),
                    fromfile=str(ref_path),
                    tofile=str(output_path),
                )
                sys.stdout.writelines(diff_lines)
                assert False


@pytest.fixture()
def assert_equals_result(request, tmp_path):
    file_path = Path(request.module.__file__).parent
    file_path /= (
        Path("refs") / Path(request.module.__file__).stem / request.node.parent.name
    )

    file_path.mkdir(parents=True, exist_ok=True)

    filename = f"{request.node.name}.json"
    filename = filename.replace("\\", "").replace("/", "")

    ref_path = file_path / filename

    output_path = tmp_path / filename
    return lambda data: _assert_equals_result(ref_path, output_path, data)


def _assert_equals_file(ref_path: Path, output_path: Path, data: Path):
    assert data.exists()

    ref_path = Path(f"{ref_path}{data.suffix}")
    output_path = Path(f"{output_path}{data.suffix}")

    if not ref_path.exists():
        shutil.copyfile(data, ref_path)
    else:
        shutil.copyfile(data, output_path)
        if data.suffix == ".nc":
            assert_identically_close(
                xr.open_dataset(ref_path), xr.open_dataset(output_path)
            )
        elif data.suffix == ".netcdf":
            assert_identically_close(
                xr.open_dataarray(ref_path), xr.open_dataarray(output_path)
            )
        else:
            assert filecmp.cmp(ref_path, output_path, shallow=False)


@pytest.fixture()
def assert_equals_file(request, tmp_path):
    file_path = Path(request.module.__file__).parent
    file_path /= (
        Path("refs") / Path(request.module.__file__).stem / request.node.parent.name
    )

    file_path.mkdir(parents=True, exist_ok=True)

    filename = request.node.name.replace("\\", "").replace("/", "")
    ref_path = file_path / filename
    output_path = tmp_path / filename

    return lambda data: _assert_equals_file(ref_path, output_path, data)

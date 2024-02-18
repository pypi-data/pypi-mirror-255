from pathlib import Path

import pytest

import mfire.utils.mfxarray as xr
from tests.composite.factories import BaseCompositeFactory
from tests.functions_test import assert_identically_close


class TestBaseComposite:
    def test_hash(self):
        compo = BaseCompositeFactory()
        assert compo.hash == "99914b932bd37a50b983c5e7c90ae93"

    def test_new(self):
        compo = BaseCompositeFactory()
        compo._keep_data = True

        new_compo = compo.new()
        assert new_compo._keep_data is True

    def test_compute(self):
        data = xr.DataArray([1])
        compo = BaseCompositeFactory(data=data)
        assert_identically_close(compo.compute(), data)
        assert_identically_close(compo.compute(), data)

        compo._keep_data = False
        assert_identically_close(compo.compute(), data)
        assert compo.compute() is None

    def test_reset(self):
        data = xr.DataArray([1])
        compo = BaseCompositeFactory(data=data)
        compo.reset()

        assert compo.compute() is None

    def test_clean(self, test_file):
        path = Path(test_file.name)

        data = xr.DataArray([1])
        compo = BaseCompositeFactory(data=data)
        compo._cached_filenames = {"data": path}

        compo.compute()

        assert path.exists()
        compo.clean()
        assert not path.exists()

    @pytest.mark.parametrize("test_file", [{"extension": "netcdf"}], indirect=True)
    def test_load_cache(self, test_file):
        compo = BaseCompositeFactory()
        compo._cached_filenames = {"data": Path("file")}

        with pytest.raises(
            FileNotFoundError,
            match="BaseCompositeFactory not cached, you must compute it before.",
        ):
            compo.load_cache()

        path = Path(test_file.name)
        compo._cached_filenames = {"data": path}
        assert compo.load_cache() is False
        assert compo._data is None

        data = xr.DataArray([1])
        data.to_netcdf(path)
        assert compo.load_cache() is True
        assert_identically_close(compo._data, data)

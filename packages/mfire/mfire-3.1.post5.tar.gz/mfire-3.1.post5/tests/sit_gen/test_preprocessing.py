from pathlib import Path

import mfire.utils.mfxarray as xr
from mfire.settings import TEXT_ALGO
from mfire.sit_gen.preprocessing import MinMaxScaler, Normalizer, open_preprocessing
from tests.functions_test import assert_identically_close


class TestPreprocessing:
    # Values to test
    ds = xr.Dataset(
        data_vars={
            "t2m": ("time", [285, 286, 287]),
            "msl": ("time", [100500, 101000, 1015000]),
        },
        coords={"time": [0, 1, 2]},
    )

    def test_normalizer(self):
        # Usual fit - transform usage
        normalizer = Normalizer()
        # fit
        normalizer.fit(self.ds)
        assert str(normalizer) == (
            "<class 'mfire.sit_gen.preprocessing.Normalizer'>\n"
            "         mean            std\n"
            "t2m     286.0       0.816497\n"
            "msl  405500.0  430981.631472"
        )
        # transform
        norm_ds = normalizer.transform(self.ds).round(4)
        assert_identically_close(
            norm_ds,
            xr.Dataset(
                data_vars={
                    "t2m": ("time", [-1.2247, 0.0, 1.2247]),
                    "msl": ("time", [-0.7077, -0.7065, 1.4142]),
                },
                coords=self.ds.coords,
            ),
        )
        # csv export
        fname = Path("normalizer.csv")
        normalizer.to_csv(fname)
        assert fname.is_file()
        # csv import
        new_normalizer = Normalizer.read_csv(fname)
        assert new_normalizer == normalizer
        if fname.is_file():
            fname.unlink()

    def test_minmaxscaler(self):
        # Usual fit - transform usage
        scaler = MinMaxScaler()
        # fit
        scaler.fit(self.ds)
        assert str(scaler) == (
            "<class 'mfire.sit_gen.preprocessing.MinMaxScaler'>\n"
            "          min        max\n"
            "t2m     285.0      287.0\n"
            "msl  100500.0  1015000.0"
        )
        # transform
        scaled_ds = scaler.transform(self.ds).round(7)
        assert_identically_close(
            scaled_ds.round(7),
            xr.Dataset(
                data_vars={
                    "t2m": ("time", [0.0, 0.5, 1.0]),
                    "msl": ("time", [0.0, 0.0005467, 1.0]),
                },
                coords=self.ds.coords,
            ),
        )
        # csv export
        fname = Path("scaler.csv")
        scaler.to_csv(fname)
        assert fname.is_file()
        # csv import
        new_scaler = MinMaxScaler.read_csv(fname)
        assert new_scaler == scaler
        if fname.is_file():
            fname.unlink()

    def test_open_preprocessing(self):
        # fronts
        fronts_normalizer = open_preprocessing(
            TEXT_ALGO["sitgen_fronts"]["generic"]["normalizer"]
        )
        norm_ds = fronts_normalizer.transform(self.ds).round(5)
        assert_identically_close(
            norm_ds,
            xr.Dataset(
                data_vars={
                    "t2m": ("time", [-0.13187, -0.06223, 0.00741]),
                    "msl": ("time", [-0.87124, -0.34422, 963.04853]),
                },
                coords=self.ds.coords,
            ),
        )

        # anticyclone - depression
        ad_normalizer = open_preprocessing(
            TEXT_ALGO["sitgen_ad"]["generic"]["normalizer"]
        )
        norm_ds = ad_normalizer.transform(self.ds)
        assert_identically_close(
            norm_ds.round(5),
            xr.Dataset(
                data_vars={
                    "t2m": ("time", [-0.13187, -0.06223, 0.00741]),
                    "msl": ("time", [-0.87124, -0.34422, 963.04853]),
                },
                coords=self.ds.coords,
            ).round(5),
        )

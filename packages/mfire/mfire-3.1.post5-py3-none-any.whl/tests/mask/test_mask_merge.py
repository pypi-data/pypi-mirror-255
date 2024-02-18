import mfire.utils.mfxarray as xr
from mfire.mask.mask_merge import MaskMerge, MergeArea
from tests.functions_test import assert_identically_close

xr.set_options(keep_attrs=True)


class TestManageMerge:
    def create_ds(self, numbers):
        """
        MaskMerge tests
        create several dataset in a list
        and create the merged of all them
        via the "natural" xarray merge
        as a reference for merging
        Args:
            numbers : number of dataset in the list
        return
           list of dataset
           dataset as merged of the list
        """
        mergings = []
        for number in range(numbers):
            # define data with variable attributes
            data_vars = {
                "velocity"
                + str(number): (
                    ["time"],
                    [number, 2 * number],
                    {"units": "m/s", "long_name": "free-fall velocity"},
                )
            }

            # define coordinates
            coords = {"time": (["time"], [1, 2])}
            # define global attributes
            attrs = {"creationnumber": number}
            # create dataset
            ds = xr.Dataset(data_vars=data_vars, coords=coords, attrs=attrs)
            mergings.append(ds)
        ref_ds = xr.merge(mergings)
        return mergings, ref_ds

    def test_manage_merge(self):
        # test with a list of dataset under the bloc size
        tout = MaskMerge()
        infra = tout.BLOCK_NBR // 2
        mergings, ref_manage_merge = self.create_ds(infra)
        for merging in mergings:
            tout.merge(merging)
        result = tout.get_merge()
        xr.testing.assert_equal(result, ref_manage_merge)
        # test with a list of dataset over the bloc size
        tout = MaskMerge()
        supra = tout.BLOCK_NBR + infra

        mergings, ref_manage_merge = self.create_ds(supra)
        for merging in mergings:
            tout.merge(merging)
        result = tout.get_merge()
        xr.testing.assert_equal(result, ref_manage_merge)


class TestMergeArea:
    def create_da(self):
        valeurs = [[[0, 1], [2, 3]], [[4, 5], [6, 7]], [[8, 9], [10, 11]]]
        da = xr.DataArray(
            data=valeurs,
            coords={"lat": [45, 46], "lon": [0, 1], "id": ["id1", "id2", "id3"]},
            dims=["id", "lat", "lon"],
            name="grille",
        )
        # define data with variable attributes
        data_vars = {
            "grille": (
                ["id", "lat", "lon"],
                [[[4.0, 5], [6, 7]], [[8, 9], [10, 11]]],
                {"units": "m/s", "long_name": "free-fall velocity"},
            )
        }

        # define coordinates
        coords = {
            "lat": (["lat"], [45, 46]),
            "lon": (["lon"], [0, 1]),
            "id": (["id"], ["neoA", "neoB"]),
            "areaName": (["id"], ["neoNomA", "neoNomB"]),
            "areaType": (["id"], ["neoTypeA", "neoTypeB"]),
        }
        # create dataset
        ref_ds = xr.Dataset(data_vars=data_vars, coords=coords)
        return da, ref_ds

    def test_merge_area(self):
        dgrid, ref_merge_area = self.create_da()
        merged = MaskMerge()
        mergearea = MergeArea(dgrid, merged)
        nz = [
            {
                "base": ["id1", "id2"],
                "id": "neoA",
                "name": "neoNomA",
                "areaType": "neoTypeA",
            },
            {
                "base": ["id1", "id3"],
                "id": "neoB",
                "name": "neoNomB",
                "areaType": "neoTypeB",
            },
        ]
        for n in nz:
            mergearea.compute(n)
        result = merged.get_merge()
        print(result)
        assert_identically_close(result, ref_merge_area)

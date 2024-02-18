import mfire.utils.mfxarray as xr

xr.set_options(keep_attrs=True)


class MaskMerge:
    """
    overload of xr.merge that merge by block

    It takes a pretty long time to merge a lot of dataset into a single one
    but by merging by block and then merge to a single one, it's faster

            CAUTION : get_merged must be call to get the final merged dataset
    """

    BLOCK_NBR = 30

    def __init__(self):
        """
        a initial empty final dataset merged
        and a temporaray dataset dpartial
        set the group size "bloc"
        """
        self.count = 0
        self.merged = xr.Dataset()
        self.dpartial = xr.Dataset()

    def merge(self, merging: xr.Dataset):
        """
        each dataset is merged into dpartial
        every "bloc", dpartial is merged into merged
        """
        self.dpartial = xr.merge([self.dpartial, merging])
        self.count += 1
        if self.count % self.BLOCK_NBR == 0:
            self.merged = xr.merge([self.merged, self.dpartial])
            self.dpartial = xr.Dataset()

    def get_merge(self):
        """
        finally, return the merged dataset
        primary merged the pending dpartial
        """
        if self.count % self.BLOCK_NBR > 0:
            self.merged = xr.merge([self.merged, self.dpartial])
            self.dpartial = xr.Dataset()
            self.count = 0
        return self.merged


class MergeArea:
    """
    merge into general set of zones
    the union of 2 zones
    for used in a comprehension list
    """

    def __init__(self, dgrid: xr.Dataset, managedout: MaskMerge):
        """
        Args:
            dgrid (xr.Dataset): grille
            managedout (MaskMerge) : Les masques déjà créés
        """
        self.dgrid = dgrid
        self.managedout = managedout

    def compute(self, new_zone):
        """Permet de merger les zones.

        Args:
            new_zone (dict): paires de zones à créer
        Returns:
            rien mais ajoute dans managedout les zones fusionnées.
        """
        dtemp = self.dgrid.sel(id=new_zone["base"]).max("id")
        dtemp = dtemp.expand_dims(dim="id").assign_coords(id=[new_zone["id"]])
        dtemp["areaName"] = (("id"), [new_zone["name"]])
        dtemp["areaType"] = (("id"), [new_zone["areaType"]])
        self.managedout.merge(dtemp)

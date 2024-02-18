from __future__ import annotations

import time
from multiprocessing import current_process
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel

import mfire.utils.mfxarray as xr
from mfire.settings import Settings, get_logger
from mfire.utils import MD5
from mfire.utils.exception import LoaderError
from mfire.utils.xr_utils import ArrayLoader

# Logging
LOGGER = get_logger(name="composite.base.mod", bind="composite.base")


class BaseComposite(BaseModel):
    """This abstract class implements the Composite design pattern,
    i.e. a tree-like structure of objects to be produced.

    Example: I have a hazard_id, which contains multiple levels of risks;
    each level contains elementary events; each event is defined by fields
    and masks. To produce each of the mentioned elements, we need to produce
    the child elements.

    This class gathers the attributes and methods common to Field, Geo, Element,
    Level, Component, etc.
    """

    _data: Optional[Union[xr.DataArray, xr.Dataset]] = None
    _cached_filenames: dict = {}

    # Whether to keep the computed data in memory. Warning: Do not keep too much data
    # in memory to avoid memory overflow. Defaults to False.
    _keep_data: bool = False

    class Config:
        """This Config class controls the behavior of pydantic"""

        underscore_attrs_are_private = True
        arbitrary_types_allowed = True
        copy_on_model_validation = False

    @property
    def _cached_attrs(self) -> dict:
        return {"data": ArrayLoader}

    @property
    def cached_basename(self) -> str:
        """Property created to define the basename of the cached file

        Returns:
            str: self cached file's basename
        """
        return f"{self.__class__.__name__}/{self.hash}"

    def cached_filename(self, attr: str = "data") -> Path:
        """Property created to define the filename of the cached file
        and creating the directory if it doesn't exist

        Returns:
            str: self cached file's full name
        """
        if self._cached_filenames.get(attr, None) is None:
            self._cached_filenames[attr] = (
                Settings().cache_dirname / f"{self.cached_basename}_{attr}"
            )
        return self._cached_filenames[attr]

    def is_cached(self) -> bool:
        """Method to know whether a composite object is already cached or not

        Returns:
            bool: Whether the object is cached.
        """
        return all(self.cached_filename(attr).is_file() for attr in self._cached_attrs)

    def load_cache(self) -> bool:
        """Load a given file if a filename is given
        or load a cached file if it exists.

        Raises:
            FileNotFoundError: Raised if no filename is given and no file is cached.
        """
        if not self.is_cached():
            raise FileNotFoundError(
                f"{self.__class__.__name__} not cached, you must compute it before."
            )

        for attr, loader_class in self._cached_attrs.items():
            filename = self.cached_filename(attr)
            try:
                loader = loader_class(filename=filename)
                setattr(self, f"_{attr}", loader.load())
            except (LoaderError, FileNotFoundError) as excpt:
                LOGGER.warning(f"Exception caught during cache loading : {repr(excpt)}")
                return False
        return True

    def dump_cache(self):
        """
        Dump the self._data into a netCDF file. If no filename is provided, it is
        dumped to the cache.
        """
        for attr, loader_class in self._cached_attrs.items():
            filename = self.cached_filename(attr)
            if not filename.is_file():
                filename.parent.mkdir(parents=True, exist_ok=True)
                tmp_hash = MD5(f"{current_process().name}-{time.time()}").hash
                tmp_filename = Path(f"{filename}{tmp_hash}.tmp")
                try:
                    loader = loader_class(filename=tmp_filename)
                    dump_status = loader.dump(data=getattr(self, f"_{attr}"))
                    err_msg = ""
                except LoaderError as excpt:
                    dump_status = False
                    err_msg = excpt
                if dump_status:
                    tmp_filename.rename(filename)
                else:
                    LOGGER.warning(
                        f"Failed to dump attribute '_{attr}' to tmp cached file "
                        f"{tmp_filename} using {loader_class}. {err_msg}"
                    )

    def _compute(self, **_kwargs) -> Optional[Union[xr.DataArray, xr.Dataset]]:
        """
        Private method to actually produce the composite data.

        Returns:
            xr.DataArray: Computed data.
        """
        return self._data

    def compute(
        self, force: bool = False, **kwargs
    ) -> Optional[Union[xr.DataArray, xr.Dataset]]:
        """
        Generic compute method created to provide computed composite's data.
        If the self._data already exists or if the composite's data has already been
        cached, we use what has already been computed.
        Otherwise, we use the private _compute method to compute the composite's data.

        Returns:
            xr.DataArray: Computed data.
        """
        if self._data is None:
            if force or not (self.is_cached() and self.load_cache()):
                self._data = self._compute(**kwargs)
                if kwargs.get("save_cache", Settings().save_cache):
                    self.dump_cache()

        if self._keep_data:
            # If we want to keep the self._data, we return it as is
            return self._data

        # Otherwise, we clear it and return the result
        tmp_da = self._data
        self._data = None
        return tmp_da

    def reset(self):
        """
        Reset the self._data and self._cached_filename.
        Use this when attributes are changed on the fly.
        """
        self._data = None
        for attr in self._cached_filenames:
            self._cached_filenames[attr] = None

    def clean(self):
        """
        Clean the cache and reset the object.
        Use this when attributes are changed on the fly.
        """
        if self.is_cached():
            for filename in self._cached_filenames.values():
                filename.unlink()
        self.reset()

    @property
    def hash(self) -> str:
        """
        Hash of the object.

        Returns:
            str: Hash.
        """
        return MD5(obj=self.dict(), length=-1).hash

    def new(self) -> BaseComposite:
        """
        Create a brand new - not computed yet - copy of self.

        Returns:
            BaseComposite: Not computed copy of self.
        """
        return self.__class__(**self.dict())

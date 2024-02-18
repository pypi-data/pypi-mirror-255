from __future__ import annotations

import json
from datetime import datetime, timedelta
from io import IOBase
from pathlib import Path
from typing import Any, Union

import numpy as np
from pydantic import BaseModel

from mfire.utils import recursive_are_equals

Jsonable = Union[
    dict, list, tuple, str, int, float, bool, datetime, timedelta, BaseModel
]


def prepare_json(item):
    prepare = json.dumps(
        item,
        ensure_ascii=False,
        cls=MFireJSONEncoder,
        indent=0,
    )
    return json.loads(prepare)


class MFireJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder made to easily encode types commonly used in MFire:
    - pydantic.BaseModel
    - datetime.datetime (and custom Datetime in extenso)
    - datetime.timedelta (and custom Timedelta in extenso)
    """

    def default(self, o: Any) -> Any:
        if isinstance(o, BaseModel):
            return json.loads(o.json(encoder=self.default))
        if isinstance(o, (datetime, timedelta, np.datetime64, np.timedelta64, Path)):
            return str(o)
        if isinstance(o, slice):
            bounds = [o.start, o.stop, o.step]
            return [b for b in bounds if b is not None]
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)


class JsonFile:
    """Custom class for handling text or binary files containing JSON documents.
    This custom class uses the MFireJSONEncoder by default for the dumping process.

    Args:
        filename (Union[str, Path]): JSON filename
    """

    filename: Union[str, Path, IOBase]

    def __init__(self, filename: Union[str, Path, IOBase]):
        self.filename = filename

    def load(self, **kwargs) -> Jsonable:
        """Opens a text or binary file containing a JSON document and deserialize it
        to a Python object.

        Returns:
            Jsonable: Deserialized object
        """
        if isinstance(self.filename, IOBase):
            return json.load(self.filename, **kwargs)

        with open(self.filename, "r") as fp:
            return json.load(fp, **kwargs)

    def dump(self, obj: Jsonable, **kwargs):
        """Serialize obj as a JSON formatted and export it to a text file.
        It uses the MFireJSONEncoder by default.

        Args:
            obj (Jsonable): Serialized object.
        """
        encoder = kwargs.pop("cls", MFireJSONEncoder)
        indent = kwargs.pop("indent", 0)
        ensure_ascii = kwargs.pop("ensure_ascii", False)

        if isinstance(self.filename, IOBase):
            self.filename.write(
                json.dumps(
                    obj, ensure_ascii=ensure_ascii, cls=encoder, indent=indent, **kwargs
                )
            )
        else:
            with open(self.filename, "w") as fp:
                json.dump(
                    obj,
                    fp,
                    ensure_ascii=ensure_ascii,
                    cls=encoder,
                    indent=indent,
                    **kwargs,
                )
                fp.close()

    def __eq__(self, other: Union[JsonFile, Path]) -> bool:
        return self.is_equal_to(other)

    def is_equal_to(
        self, other: Union[JsonFile, Path], verbose: int = 2, **kwargs
    ) -> bool:
        """Compare the differences between two JSON files and highlight the differences
        if needed.

        Args:
            other (Union[JsonFile,Path]): Another JSON file.
            verbose (int, optional): Level of description of the differences.
                Defaults to 2.

        Returns:
            bool: True if there are equals, False otherwise.
        """
        # Load JSON data from the left file
        with open(self.filename) as lfp:
            left_dico = json.load(lfp)

        # Load JSON data from the right file
        other_filename = other.filename if isinstance(other, JsonFile) else other
        with open(other_filename) as rfp:
            right_dico = json.load(rfp)

        # Compare the dictionaries and return the result
        return recursive_are_equals(
            left=left_dico,
            right=right_dico,
            index_list="",
            verbose=verbose,
            **kwargs,
        )

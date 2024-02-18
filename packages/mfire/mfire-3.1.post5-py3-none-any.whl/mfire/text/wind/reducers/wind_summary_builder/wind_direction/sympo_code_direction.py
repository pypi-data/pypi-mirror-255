from __future__ import annotations

from typing import Dict, Optional


class SympoCodeDirection:
    """SympoCodeDirection class."""

    DIRECTION_NOT_SET: str = "Direction not set"
    MAPPING: Dict[int, str] = {
        0: "Nord",
        1: "Nord-Nord-Est",
        2: "Nord-Est",
        3: "Est-Nord-Est",
        4: "Est",
        5: "Est-Sud-Est",
        6: "Sud-Est",
        7: "Sud-Sud-Est",
        8: "Sud",
        9: "Sud-Sud-Ouest",
        10: "Sud-Ouest",
        11: "Ouest-Sud-Ouest",
        12: "Ouest",
        13: "Ouest-Nord-Ouest",
        14: "Nord-Ouest",
        15: "Nord-Nord-Ouest",
    }
    UNKNOWN_DIRECTION: str = "Unknown direction"

    @classmethod
    def get_direction_from_sympo_code(cls, sympo_code: Optional[int]) -> str:
        """Get the textual direction from a sympo code."""
        if sympo_code is None:
            return cls.DIRECTION_NOT_SET
        return cls.MAPPING.get(sympo_code, cls.UNKNOWN_DIRECTION)

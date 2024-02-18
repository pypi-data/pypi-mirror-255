"""mfire.mask module

This module handles everything related to the mask

"""
from mfire.mask.mask_processor import MaskProcessor
from mfire.mask.fusion import extract_area_name

__all__ = [
    "MaskProcessor",
    "extract_area_name",
]

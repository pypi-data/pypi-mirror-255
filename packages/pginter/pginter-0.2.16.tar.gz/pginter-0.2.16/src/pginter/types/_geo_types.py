"""
_geo_types.py
04. February 2023

types for the geometry manager

Author:
Nilusink
"""
from enum import Enum


class Layout(Enum):
    Absolute = "absolute"
    Pack = "pack"
    Grid = "grid"


class GeoNotes(Enum):
    SetNormal = 0
    SetHover = 1
    SetActive = 2
    RequireRedraw = 3
    RequireRecalc = 4

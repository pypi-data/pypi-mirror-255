"""
_binds.py
25. May 2023

Defines Enums for all possible bind types

Author:
Nilusink
"""
from enum import Enum


class FrameBind(Enum):
    """
    the string values represent the tkinter bind names
    """
    active_move = "<B1-Motion>"
    active_release = "<ButtonRelease-1>"
    active = "<Button-1>"

    hover = "<Enter>"
    hover_release = "<Leave>"
    hover_move = "<H-Motion>"

    mousewheel = "<MouseWheel>"

    key_return = "<Return>"


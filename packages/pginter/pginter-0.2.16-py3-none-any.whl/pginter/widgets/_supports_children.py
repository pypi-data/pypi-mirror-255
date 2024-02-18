"""
_supports_children.py
04. February 2023

All widgets which support parenting should inherit this

Author:
Nilusink
"""
import typing as tp


class SupportsChildren:
    _children: list[tp.Any] = ...

    def __init__(self) -> None:
        self._children = []

    def add_child(self, child: tp.Any) -> None:
        """
        add a child to the collection
        """
        self._children.append(child)

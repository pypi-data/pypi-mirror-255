"""
_funcs.py
05. February 2023

a few generic useful functions

Author:
Nilusink
"""
import typing as tp


def arg_or_default(
        value: tp.Any,
        default_value: tp.Any,
        check_if: tp.Any = ...
) -> tp.Any:
    """
    :param value: the value to check
    :param default_value: what the value should be if it equals `check_if`
    :param check_if: what to check for
    """
    return default_value if value is check_if else value


def point_in_box(
        point: tuple[int, int],
        box: tuple[int, int, int, int]
) -> bool:
    """
    check if a point is inside a box

    :param point: point to check
    :param box: x, y width, height
    """
    return all([
        # x collision
        box[0] <= point[0],
        point[0] <= box[0] + box[2],

        # y collision
        box[1] <= point[1],
        point[1] <= box[1] + box[3]
    ])


"""
_surface_frame.py
24. May 2023

A pygame surface to draw on

Author:
Nilusink
"""
from ._frame import Frame
import typing as tp
import pygame as pg


class SurfaceFrame(Frame):
    """
    A pygame surface to draw on
    """
    _surface: pg.Surface
    _in_loop_func: tp.Callable[[pg.Surface], None] = ...

    def __init__(
            self,
            parent: tp.Union["Frame", tp.Any],
            width: int = ...,
            height: int = ...,
            margin: int = ...,
            min_width: int = ...,
            min_height: int = ...,
    ) -> None:
        self._surface = pg.Surface(
            (
                (1 if min_width is ... else min_width) if width is ... else width,
                (1 if min_height is ... else min_height) if height is ... else height
            ),
            pg.SRCALPHA
        )

        # limit the arguments that get passed to the parent
        super().__init__(
            parent=parent,
            width=width,
            height=height,
            margin=margin,
            min_width=min_width,
            min_height=min_height
        )

    def in_loop(self, func: tp.Callable[[pg.Surface], None]) -> None:
        """
        Execute a task in the loop. The function argument is the pygame surface.
        """
        if isinstance(func, tp.Callable):
            self._in_loop_func = func

    @property
    def surface(self) -> pg.Surface:
        return self._surface

    def draw(self, surface: pg.Surface) -> None:
        """
        insert the surface
        """
        if self._in_loop_func is not ...:
            self._in_loop_func(self._surface)

        surface.blit(self._surface, (self._x, self._y))

"""
_pg_root.py
04. February 2023

the root of the window

Author:
Nilusink
"""
from concurrent.futures import ThreadPoolExecutor as Pool, Future
from .widgets import GeometryManager
from .theme import ThemeManager
from time import perf_counter
from .types import *
import typing as tp
import pygame as pg
import os.path


DEFAULT_TITLE: str = "Window"
DEFAULT_ICON: str = os.path.dirname(__file__) + "/icon.png"


class _TimeoutCandidate[T](tp.TypedDict):
    timeout_left: float
    function: tp.Callable[[tp.Any], T]
    future: Future[T]
    args: tuple[tp.Any, ...]
    kwargs: dict[str, tp.Any]


class PgRoot(GeometryManager):
    _focus_item: GeometryManager | None = None
    _running: bool = True
    _theme: ThemeManager = ...
    __background: pg.Surface = ...
    layout_params: BetterDict = ...
    _min_size: tuple[int, int] = ...
    _bg_configured: bool = False
    _mouse_pos: tuple[int, int] = ...
    _mouse_scroll: list[int, int]
    _max_framerate: int = ...
    _requires_recalc: bool = True

    __timeouts: list[_TimeoutCandidate]
    _last_it_call: float
    _tpool: Pool

    show_wireframe: bool = False
    smooth_scaling: bool = False
    _last_resize: float = 0

    def __init__(
            self,
            title: str = ...,
            icon_path: str = ...,
            size: tuple[int, int] = ...,
            bg_color: Color = ...,
            padding: int = 0,
            margin: int = 0,
            max_framerate: int = 30
    ) -> None:
        self._last_it_call = perf_counter()
        self._max_framerate = max_framerate
        self._tpool = Pool(max_workers=10)
        self.__timeouts = []
        self._mouse_scroll = [0, 0]

        super().__init__()
        self._theme = ThemeManager()
        self._theme.notify_on(ThemeManager.NotifyEvent.theme_reload, self.notify)
        self._min_size = (0, 0)

        # args
        self._bg_configured = bg_color is not ...
        self._bg = self._theme.root.bg.hex if bg_color is ... else bg_color

        self._layout_params = BetterDict({
            "padding": padding,
            "margin": margin,
        })

        # pg init
        pg.init()
        pg.font.init()
        self._clk = pg.time.Clock()

        if size is not ...:
            self.__background = pg.display.set_mode(size, flags=pg.RESIZABLE)

        else:
            self.__background = pg.display.set_mode(flags=pg.RESIZABLE)

        # set icon and caption
        pg.display.set_caption(DEFAULT_TITLE if title is ... else title)
        img = pg.image.load(
            DEFAULT_ICON if icon_path is ... else icon_path, "icon"
        )
        pg.display.set_icon(img)

    # config
    @property
    def title(self) -> str:
        return pg.display.get_caption()[0]

    @title.setter
    def title(self, value: str) -> None:
        pg.display.set_caption(value)

    @property
    def theme(self) -> ThemeManager:
        return self._theme

    @property
    def mouse_pos(self) -> tuple[int, int]:
        return self._mouse_pos

    @property
    def root(self) -> tp.Self:
        return self

    @property
    def mouse_scroll(self) -> None:
        return tuple(self._mouse_scroll)

    @property
    def _height_configured(self) -> bool:
        return True

    @property
    def _width_configured(self) -> bool:
        return True

    @property
    def _height(self) -> int:
        return pg.display.get_window_size()[1]

    @_height.setter
    def _height(self, *_) -> None:
        """
        value should not be set, but no error should occur
        """
        pass

    @property
    def _width(self) -> int:
        return pg.display.get_window_size()[0]

    @_width.setter
    def _width(self, *_) -> None:
        """
        value should not be set, but no error should occur
        """
        pass

    def get_focus(self) -> GeometryManager | None:
        """
        get the currently focused item
        """
        return self._focus_item

    def set_focus(
            self,
            widget: tp.Union["GeometryManager", None, tp.Any] = None
    ) -> None:
        """
        set the focused item
        """
        if self._focus_item is not None:
            self._focus_item.stop_focus()

        if widget is not None:
            widget.set_focus()
            self._focus_item = widget

    def notify_focus(self, widget: tp.Union["GeometryManager", None] = None):
        """
        notify the root that a widget has been set as focus
        """
        if self._focus_item != widget:
            self.set_focus(widget)

    # interfacing
    def notify(self, event: ThemeManager.NotifyEvent, _info=...) -> None:
        """
        gets called by another class
        """
        match event:
            case ThemeManager.NotifyEvent.theme_reload:
                # the theme has been reloaded
                if not self._bg_configured:
                    self._bg = self.theme.root.bg.rgba

            case GeoNotes.RequireRecalc:
                self._requires_recalc = True

    # pygame stuff
    def _event_handler(self) -> None:
        """
        handle the events raised by pygame
        """
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    self._running = False

                case pg.KEYDOWN:
                    if self._focus_item is not None:
                        self._focus_item.notify(
                            KeyboardNotifyEvent.key_down,
                            event
                        )

                case pg.KEYUP:
                    if self._focus_item is not None:
                        self._focus_item.notify(
                            KeyboardNotifyEvent.key_up,
                            event
                        )

                case pg.MOUSEWHEEL:
                    self._mouse_scroll[0] -= event.x
                    self._mouse_scroll[1] -= event.y

                case pg.VIDEORESIZE:  # window size changed
                    if self.smooth_scaling:
                        self._requires_recalc = True

                    else:
                        now = perf_counter()
                        delta = now - self._last_resize
                        self._last_resize = now

                        if delta > .2:
                            self._requires_recalc = True
                #     width, height = event.size
                #
                #     print("updating size: ", (width, height), "\t", self._min_size)
                #
                #     width = max([width, self._min_size[0]])
                #     height = max([height, self._min_size[1]])
                #
                #     # self.__background = pg.display.set_mode((width, height), flags=pg.RESIZABLE | pg.HWSURFACE | pg.DOUBLEBUF)

        self._mouse_pos = pg.mouse.get_pos()

        self._notify_child_active_hover(self.mouse_pos)

    def update_idletasks(self) -> None:
        """
        updates all the functional tasks
        """
        self._event_handler()

        # handle timeouts
        for to in self.__timeouts.copy():
            # calculate time since last function call
            now = perf_counter()
            delta = now - self._last_it_call
            self._last_it_call = now

            # remove time from timeout
            to["timeout_left"] -= delta * 1000

            # if the timeout is finished, execute the function
            if to["timeout_left"] <= 0:
                # create a function that populates the timeout future's result
                # with the function return value
                def curr_func():
                    to["future"].set_result(to["function"](
                        *to["args"], **to["kwargs"]
                    ))

                # submit the created function to the threadpool
                # and remove it from the active timeouts
                self._tpool.submit(curr_func)
                self.__timeouts.remove(to)

    def update(self) -> None:
        """
        update the screen
        """
        self.__background.fill(self._bg)

        if self._requires_recalc:
            self._requires_recalc = False
            self.calculate_geometry()

        for child, params in self._child_params:
            child.draw(self.__background)

        pg.display.flip()

    def mainloop(self):
        """
        run the windows main loop
        """
        while self._running:
            self.update_idletasks()
            self.update()

            self._clk.tick(self._max_framerate)

    def calculate_size(self) -> tuple[int, int]:
        """
        calculate how big the container should be
        """
        # make sure the geometry is up-to-date
        return pg.display.get_window_size()

    # tool functions
    def after[T](
            self,
            timeout: int,
            function: tp.Callable[[tp.Any], T],
            *args,
            **kwargs
    ) -> Future[T]:
        """
        calls the given function after timeout milliseconds

        :param timeout: timeout in milliseconds
        :param function: the function to call
        :param args: the given functions positional arguments
        :param kwargs: the given functions keyword arguments
        :returns: a future with the function's result
        """
        n_future = Future[T]()

        self.__timeouts.append({
            "timeout_left": timeout,
            "function": function,
            "future": n_future,
            "args": args,
            "kwargs": kwargs
        })

        return n_future

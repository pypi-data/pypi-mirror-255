"""
_manager.py
04. February 2023

The built-in theme manager

Author:
Nilusink
"""
from enum import Enum
from ..types import *
import typing as tp
import json
import os


DEFAULT_THEME: str = os.path.dirname(__file__) + "/themes/default.json"


class Appearance(Enum):
    dark = 0
    light = 1


class _NotifyEvent(Enum):
    theme_reload = 0


class ThemeManager:
    """
    the build-in theme manager
    """
    Appearance = Appearance
    NotifyEvent = _NotifyEvent
    _appearance: Appearance = Appearance.dark
    _notify_on: dict[NotifyEvent, list[tp.Callable]] = ...
    _config: dict[str, str | dict] = ...
    _theme_path: str = ...
    instance = ...

    def __new__(cls, *args, **kwargs):
        """
        only on instance of a theme manager should ever exist
        """
        if cls.instance is ...:
            cls.instance = super().__new__(cls, *args, **kwargs)

        return cls.instance

    def __init__(self, theme_path: str = ...) -> None:
        # load the theme
        self._theme_path = theme_path
        self._notify_on = {
            _NotifyEvent.theme_reload: []
        }

        self.reload_theme()

    def notify_on(self, event: NotifyEvent, who: tp.Callable) -> None:
        """
        notify the given class on events

        :param event: the event to notify on
        :param who: the class to notify
        """
        self._notify_on[event].append(who)

    def reload_theme(self) -> None:
        """
        reload the config theme
        """
        self._config = json.load(
            open(
                DEFAULT_THEME if self.theme_path is ... else self.theme_path,
                "r"
            )
        )

        # convert each color to a color class instance
        def convert_color(color):
            if isinstance(color, str):
                # differentiate between hex and rgb values
                if color.startswith("#"):
                    return Color.from_hex(color, 255)

                elif color.startswith("rgb"):
                    return Color.from_rgb(
                        *[int(val) for val in color.lstrip("rgb").split(",")]
                    )

                else:
                    raise ValueError(
                        f"Invalid color value in theme file: \"{color}\""
                    )

            # rgb values written as tuple
            elif isinstance(color, list):
                if isinstance(color[0], float) or isinstance(color[0], int):
                    return Color.from_rgb(*color)

                elif isinstance(color[0], list) or isinstance(color[0], str):
                    return convert_color(color[self._appearance.value])

            return color

        for key in self._config.copy():
            for ckey, color in self._config[key].items():
                self._config[key][ckey] = convert_color(color)

        # notify
        for element in self._notify_on[_NotifyEvent.theme_reload]:
            element(_NotifyEvent.theme_reload)

    def set_appearance(self, appearance: Appearance) -> None:
        """
        set the appearance theme

        :param appearance: must be contained in cls.appearance
        """
        if appearance in Appearance:
            self._appearance = appearance

        else:
            raise ValueError(
                f"Expected \"Appearance\", got "
                f"\"{appearance.__class__.__name__}\""
            )

        self.reload_theme()

    @property
    def theme_path(self) -> str:
        return self._theme_path

    def __getattr__(self, item: str) -> str | BetterDict:
        """
        for better accessibility
        """
        val = self._config[item]

        if isinstance(val, dict):
            return BetterDict(val)

        elif isinstance(val, str):
            return val

        else:
            raise ValueError(f"Invalid type for key \"{item}\": {type(val)}")

    def __getitem__(self, item: str) -> str | BetterDict:
        return self.__getattr__(item)


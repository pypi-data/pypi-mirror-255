"""
_style.py
11. May 2023

The style of one element

Author:
Nilusink
"""
from ._geo_types import Layout
from ._color import Color
from enum import Enum
import typing as tp


class _NotifyEvent(Enum):
    property_change = 0


class Style:
    """
    What would a UI be without styles? Correct, a terminal!
    """
    NotifyEvent = _NotifyEvent

    width: int = ...
    height: int = ...
    minWidth: int = ...
    minHeight: int = ...

    color: Color = ...
    backgroundColor: Color = ...

    layout: Layout = ...
    margin: int = ...
    padding: int = ...

    borderRadius: int = ...
    borderBottomRadius: int = ...
    borderTopRadius: int = ...
    borderLeftRadius: int = ...
    borderRightRadius: int = ...
    borderBottomLeftRadius: int = ...
    borderBottomRightRadius: int = ...
    borderTopLeftRadius: int = ...
    borderTopRightRadius: int = ...
    borderWidth: int = ...
    borderColor: Color = ...

    fontSize: int = ...

    __notifiers: list[tuple[str, tp.Callable[[NotifyEvent, str], tp.Any]]]

    def __init__(
            self,
            width: int = ...,
            height: int = ...,
            minWidth: int = ...,
            minHeight: int = ...,
            color: Color = ...,
            backgroundColor: Color = ...,
            layout: Layout = ...,
            margin: int = ...,
            padding: int = ...,
            borderRadius: int = ...,
            borderBottomRadius: int = ...,
            borderTopRadius: int = ...,
            borderLeftRadius: int = ...,
            borderRightRadius: int = ...,
            borderBottomLeftRadius: int = ...,
            borderBottomRightRadius: int = ...,
            borderTopLeftRadius: int = ...,
            borderTopRightRadius: int = ...,
            borderWidth: int = ...,
            borderColor: Color = ...,
            fontSize: int = ...,
    ) -> None:
        """
        create a style element
        """
        self.__notifiers = []

        self.width = width
        self.height = height
        self.minWidth = minWidth
        self.minHeight = minHeight
        self.color = color
        self.backgroundColor = backgroundColor
        self.layout = layout
        self.margin = margin
        self.padding = padding
        self.borderRadius = borderRadius
        self.borderBottomRadius = borderBottomRadius
        self.borderTopRadius = borderTopRadius
        self.borderLeftRadius = borderLeftRadius
        self.borderRightRadius = borderRightRadius
        self.borderBottomLeftRadius = borderBottomLeftRadius
        self.borderBottomRightRadius = borderBottomRightRadius
        self.borderTopLeftRadius = borderTopLeftRadius
        self.borderTopRightRadius = borderTopRightRadius
        self.borderWidth = borderWidth
        self.borderColor = borderColor
        self.fontSize = fontSize

    @classmethod
    def from_dict(cls, ignore_invalid: bool = False, **properties) -> tp.Self:
        """
        Create a style element from a dict.
        """
        new_instance = cls()

        for prop, value in properties.items():
            try:
                new_instance[prop] = value

            except KeyError:
                if ignore_invalid:
                    continue

                raise

        return new_instance

    @property
    def properties(self) -> list[str]:
        """
        all available style properties
        """
        out = []
        for prop in self.__dict__:
            if prop.startswith("_") or prop.endswith("_"):
                continue

            if hasattr(self, prop):
                out.append(prop)

        return out

    def overwrite(self, other: tp.Self) -> tp.Self:
        """
        "merge" two styles, choosing the "other" styles values
        for doubles
        """
        new_instance = self.__class__()
        for prop in self.properties:
            # if available, use "other" style
            if other[prop] is not ...:
                new_instance[prop] = other[prop]

            # if "other" isn't available, try own style
            elif self[prop] is not ...:
                new_instance[prop] = self[prop]

        return new_instance

    def notify_on(
            self,
            variable: str,
            callback: tp.Callable[[NotifyEvent, str], tp.Any]
    ) -> None:
        """
        notify on variable change
        """
        self.__notifiers.append((variable, callback))

    # accessibility
    def __getitem__(self, item: str) -> tp.Any:
        if item in self.properties:
            return self.__dict__[item]

        raise KeyError(f"Can't find item \"{item}\" in Style.")

    def __setitem__(self, key: str, value: tp.Any) -> None:
        if key in self.properties:
            return self.__setattr__(key, value)

        raise KeyError(f"Can't find item \"{key}\" in Style.")

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__

    def __setattr__(self, key: str, value: tp.Any) -> None:
        # border shorthands
        if key == "borderRadius":
            self.__setattr__("borderTopLeftRadius", value)
            self.__setattr__("borderTopRightRadius", value)
            self.__setattr__("borderBottomLeftRadius", value)
            self.__setattr__("borderBottomRightRadius", value)
            return

        elif key == "borderTopRadius":
            self.__setattr__("borderTopLeftRadius", value)
            self.__setattr__("borderTopRightRadius", value)
            return

        elif key == "borderBottomRadius":
            self.__setattr__("borderBottomLeftRadius", value)
            self.__setattr__("borderBottomRightRadius", value)
            return

        elif key == "borderLeftRadius":
            self.__setattr__("borderTopLeftRadius", value)
            self.__setattr__("borderBottomLeftRadius", value)
            return

        elif key == "borderRightRadius":
            self.__setattr__("borderTopRightRadius", value)
            self.__setattr__("borderBottomRightRadius", value)
            return

        if not key.endswith("__notifiers"):
            for n_key, callback in self.__notifiers:
                if n_key.lower() == key.lower():
                    callback(_NotifyEvent.property_change, n_key)

        # change regardless of notification
        self.__dict__[key] = value

    def __repr__(self) -> str:
        out = f"{super().__repr__()}: ""{\n"
        for prop in self.properties:
            out += f"\t{prop}: {self[prop]},\n"

        return out + "}\n"

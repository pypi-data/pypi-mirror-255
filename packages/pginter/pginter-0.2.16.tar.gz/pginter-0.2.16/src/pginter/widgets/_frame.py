"""
_frame.py
04. February 2023

Frame - the base widget

Author:
Nilusink
"""
from ..utils import add_corners, pil_image_to_surface
from ._geo_manager import GeometryManager
from concurrent.futures import Future
from ..theme import ThemeManager
from ..types import *
import typing as tp
import pygame as pg

# try importing pil. The user shouldn't be forced to install pil, but
# will get an error if they try to use the image widget without having it
# installed
try:
    # noinspection PyUnresolvedReferences
    from PIL import Image, ImageDraw
    PIL_EXISTS = True

except ImportError:
    PIL_EXISTS = False


if tp.TYPE_CHECKING:
    from .._pg_root import PgRoot


RES_T = tp.TypeVar("RES_T")


def display_configurify(key: str) -> str:
    """
    convert a Frame init key to it's corresponding DisplayConfig key
    """
    replaces = [
        ("bg_color", "bg"),
        ("border_bottom_left_radius", "blr"),
        ("border_bottom_right_radius", "brr"),
        ("border_top_left_radius", "ulr"),
        ("border_top_right_radius", "urr"),
    ]

    for init, config in replaces:
        if key == init:
            return config

    return key


class _Bind(tp.TypedDict):
    id: int
    event: FrameBind
    function: tp.Callable[[tp.Any], tp.Any | None]


class Frame(GeometryManager):
    """
    The base widget
    """
    __parent: tp.Union["Frame", tp.Any] = ...
    _focused: bool = False
    _binds: list[_Bind]
    style: Style = ...
    hover_style: Style = ...
    active_style: Style = ...
    _x: int = -1
    _y: int = -1
    _last_size: tuple[int, int] = ...

    _image: Image.Image

    show_wireframe: bool = False

    def __init__(
            self,
            parent: tp.Union["Frame", tp.Any],
            width: int = ...,
            height: int = ...,
            bg: Color = ...,
            layout: Layout = Layout.Absolute,
            border_radius: int = ...,
            border_bottom_radius: int = ...,
            border_top_radius: int = ...,
            border_bottom_left_radius: int = ...,
            border_bottom_right_radius: int = ...,
            border_top_left_radius: int = ...,
            border_top_right_radius: int = ...,
            border_width: int = ...,
            border_color: Color = ...,
            image: Image.Image = ...,
            margin: int = ...,
            padding: int = ...,
            min_width: int = ...,
            min_height: int = ...,
            style: Style = ...,
            active_style: Style = ...,
            hover_style: Style = ...
    ) -> None:
        """
        The most basic widget: a frame.
        When using the  style  property, all other styles will be overwritten!

        :param parent: the frames parent container
        :param width: width of the frame
        :param height: height of the frame
        :param bg: background color of the frame
        :param border_radius: border radius of the box (all four corners)
        :param border_width: how thick the border of the box should be
        :param border_color: the color of the border
        """
        # inherit show_wireframe from parent
        self.show_wireframe = parent.show_wireframe

        if image is not ... and not PIL_EXISTS:
            raise ImportError(
                "PIL needs to be installed to use the Image widget.\n"
                "\tto install PIL, use\n"
                "\t\t\"pip install pillow\""
            )

        image: Image.Image
        self._image = image

        self._binds = []

        self.style = style if style is not ... else Style()
        self.active_style = active_style if active_style\
            is not ... else Style()
        self.hover_style = hover_style if hover_style is not ... else Style()

        if min_width is not ...:
            self._width = min_width

        if min_height is not ...:
            self._height = min_height

        self.__parent = parent

        self.__parent.theme.notify_on(
            ThemeManager.NotifyEvent.theme_reload,
            self.notify
        )

        if all([
            "border_top_left_radius" in self.theme.frame,
            self.style.borderTopLeftRadius is ...
        ]):
            self.style.borderTopLeftRadius = self.theme.frame.border_top_left_radius
            if border_top_left_radius is not ...:
                self.style.borderTopLeftRadius = border_top_left_radius

        if all([
            "border_top_right_radius" in self.theme.frame,
            self.style.borderTopRightRadius is ...
        ]):
            self.style.borderTopRightRadius = self.theme.frame.border_top_right_rasdius
            if border_top_right_radius is not ...:
                self.style.borderTopRightRadius = border_top_right_radius

        if all([
            "border_bottom_left_radius" in self.theme.frame,
            self.style.borderBottomLeftRadius is ...
        ]):
            self.style.borderBottomLeftRadius = self.theme.frame.border_bottom_left_radius
            if border_bottom_left_radius is not ...:
                self.style.borderBottomLeftRadius = border_bottom_left_radius

        if all([
            "border_bottom_right_radius" in self.theme.frame,
            self.style.borderBottomRightRadius is ...
        ]):
            self.style.borderBottomRightRadius = self.theme.border_bottom_right_radius
            if border_bottom_right_radius is not ...:
                self.style.borderBottomRightRadius = border_bottom_right_radius

        # border config
        if self.style.borderWidth is ...:
            self.style.borderWidth = 0

            if "border_width" in self.theme.frame:
                self.style.borderWidth = self.theme.frame.border_width

        if margin is ...:
            margin = self.theme.frame.margin if "margin" in\
                                                self.theme.frame else 0

        if padding is ...:
            padding = self.theme.frame.padding if "padding" in\
                                                  self.theme.frame else 0

        if self.style.margin is ...:
            self.style.margin = margin

        if self.style.padding is ...:
            self.style.padding = padding

        super().__init__(layout, self.style.margin, self.style.padding)

        self.style.notify_on("margin", self.notify)
        self.style.notify_on("padding", self.notify)

        # arguments
        if width is not ... and self.style.width is ...:
            self.style.width = width

        if height is not ... and self.style.height is ...:
            self.style.height = height

        # assign to properties (for geo-manager)
        if self.style.width is not ...:
            self.width = self.style.width

        if self.style.height is not ...:
            self.height = self.style.height

        # link the style parameters to the geo-manager properties
        def update_width(*_):
            if self.style.width is not ...:
                self.width = self.style.width

        def update_height(*_):
            if self.style.height is not ...:
                self.height = self.style.height

        self.style.notify_on("width", update_width)
        self.style.notify_on("height", update_height)

        # more arguments
        if self.style.backgroundColor is ...:
            self.style.backgroundColor = self.theme.frame.bg1 if bg is ... else bg
            if isinstance(self.__parent, Frame) and \
                    self.__parent.style.backgroundColor == self.theme.frame.bg1:
                self.style.backgroundColor = self.theme.frame.bg2 if bg is ... else bg

        if border_width is not ... and self.style.borderWidth == 0:
            self.style.borderWidth = border_width

        if self.style.borderColor is ...:
            self.style.borderColor = self.theme.frame.border\
                if border_color is ... else border_color

        # border radii
        if border_radius is ... and "border_radius" in self.theme.frame:
            border_radius = self.theme.frame.border_radius

        if border_bottom_radius is ... and\
                "border_bottom_radius" in self.theme.frame:
            border_bottom_radius = self.theme.frame.border_bottom_radius

        if border_top_radius is ... and\
                "border_top_radius" in self.theme.frame:
            border_top_radius = self.theme.frame.border_top_radius

        if self.style.borderTopLeftRadius is ...:
            self.style.borderTopLeftRadius = border_radius

        if self.style.borderTopRightRadius is ...:
            self.style.borderTopRightRadius = border_radius

        if self.style.borderBottomLeftRadius is ...:
            self.style.borderBottomLeftRadius = border_radius

        if self.style.borderBottomRightRadius is ...:
            self.style.borderBottomRightRadius = border_radius

        if border_top_radius is not ...:
            if self.style.borderTopLeftRadius is ...:
                self.style.borderTopLeftRadius = border_top_radius

            if self.style.borderTopRightRadius is ...:
                self.style.borderTopRightRadius = border_top_radius

        if border_bottom_radius is not ...:
            if self.style.borderBottomLeftRadius is ...:
                self.style.borderBottomLeftRadius = border_bottom_radius

            if self.style.borderBottomRightRadius is ...:
                self.style.borderBottomRightRadius = border_bottom_radius

    @property
    def theme(self) -> ThemeManager:
        return self.__parent.theme

    @property
    def parent(self) -> tp.Union["Frame", tp.Any]:
        return self.__parent

    @property
    def root(self) -> "PgRoot":
        return self.parent.root

    def after(
            self,
            timeout: int,
            function: tp.Callable[[tp.Any], RES_T],
            *args,
            **kwargs
    ) -> Future[RES_T]:
        """
        calls the given function after timeout milliseconds

        :param timeout: timeout in milliseconds
        :param function: the function to call
        :param args: the given functions positional arguments
        :param kwargs: the given functions keyword arguments
        :returns: a future with the function's result
        """
        return self.root.after(timeout, function, *args, **kwargs)

    @property
    def focused(self) -> bool:
        return self._focused

    def set_focus(self, **kwargs):
        """
        set this item as currently focused
        """
        self._focused = True

    def stop_focus(self):
        """
        remove focus from this item
        """
        self._focused = False

    def notify_focus(self, widget: tp.Union["GeometryManager", None] = None):
        """
        notify the root that a widget has been set as focus
        """
        self.parent.notify_focus(widget)

    def configure(self, **kwargs) -> None:
        """
        configure any of the init parameters (except parent)
        """
        for key, value in kwargs.items():
            match key:
                case "width":
                    self.width = value

                case "height":
                    self.height = value

                case "min_width":
                    self._width = value

                case "min_height":
                    self._height = value

                case "border_radius":
                    self.style.borderRadius = value

                case "border_bottom_radius":
                    self.style.borderBottomRadius = value

                case "border_top_radius":
                    self.style.borderTopRadius = value

                case _:
                    # check if in display config
                    new_key = display_configurify(key)

                    if new_key in self.style:
                        if isinstance(value, type(self.style[new_key])):
                            raise TypeError(
                                f"Can't change \"{self.style[new_key]}\" to \"{value}\": "
                                f"invalid type!"
                            )

                        self.style[key] = value

                    elif key in self.layout_params:
                        if isinstance(value, type(self.style[new_key])):
                            raise TypeError(
                                f"Can't change \"{self.layout_params[new_key]}\" to \"{value}\": "
                                f"invalid type!"
                            )

                        self.layout_params[key] = value

    # interfacing
    def notify(
            self,
            event: ThemeManager.NotifyEvent | Style.NotifyEvent,
            info: tp.Any = ...
    ) -> None:
        """
        gets called by another class
        """
        match event:
            case ThemeManager.NotifyEvent.theme_reload:
                print("theme changed")

            case Style.NotifyEvent.property_change:
                print(f"style changed: {info}, new value: {self.style[info]}")

                if info in ("padding", "margin"):
                    self.layout_params[info] = self.style[info]

            case GeoNotes.RequireRecalc:
                print("rr")
                self.root.notify(GeoNotes.RequireRecalc)

            case _:
                super().notify(event, info)

    def get_size(self) -> tuple[int, int]:
        """
        get the frames size (including children)
        """
        # width
        width = self._width if self._width_configured else \
            self.assigned_width

        # height
        height = self._height if self._height_configured else \
            self.assigned_height

        return width.__floor__(), height.__floor__()

    def get_position(self) -> tuple[int, int]:
        return self._x, self._y

    def draw(self, surface: pg.Surface) -> None:
        """
        draw the frame
        """
        if hasattr(self, "debug_this"):
            print("draw")
        requires_recalc = False

        current_style = self.style

        if self.is_hover:
            current_style = self.style.overwrite(self.hover_style)

        if self.is_active:
            current_style = self.style.overwrite(self.hover_style).overwrite(
                self.active_style
            )

        self.layout_params.padding = current_style.padding
        self.layout_params.margin = current_style.margin

        if current_style.height is not ...:
            self.height = current_style.height

        else:
            self.unset_height()

        if current_style.width is not ...:
            self.width = current_style.width

        else:
            self.unset_width()

        width, height = self.get_size()
        if self._last_size is not ...:
            if self._last_size[0] != width \
                    or self._last_size[1] != height:
                requires_recalc = True

        else:
            requires_recalc = True

        self._last_size = (width, height)

        # check if the frame even exists
        if width <= 0 or height <= 0:
            # since the image doesn't affect the calculate_size function,
            # try to set the frames size through this piece of sh- code
            if self._image is not ...:
                width, height = self.get_size()
                image_width, image_height = self._image.size

                # try to reserve aspect angle
                if width <= 0 < height:
                    width = int((image_width / image_height) * height)

                if height <= 0 < width:
                    height = int((image_height / image_width) * width)

                # if no with or height has yet been set, clone the
                # original image's size
                if width <= 0:
                    width = image_width

                if height <= 0:
                    height = image_height

                if width > self._width:
                    self.width = width

                if height > self._height:
                    self.height = height

            self.root.notify(GeoNotes.RequireRecalc)
            return

        _surface = pg.Surface((width, height), pg.SRCALPHA)

        # draw the frame
        r_rect = pg.Rect((0, 0, width, height))

        pg.draw.rect(
            _surface,
            current_style.backgroundColor.irgba,
            r_rect,
            border_top_left_radius=current_style.borderTopLeftRadius,
            border_top_right_radius=current_style.borderTopRightRadius,
            border_bottom_left_radius=current_style.borderBottomLeftRadius,
            border_bottom_right_radius=current_style.borderBottomRightRadius
        )

        if self._image is not ...:
            width, height = self.get_size()
            image_width, image_height = self._image.size

            # try to reserve aspect angle
            if hasattr(self, "debug_this"):
                print("size: ", width, height)

            if width <= 0 < height:
                width = int((image_width / image_height) * height)

            if height <= 0 < width:
                height = int((image_height / image_width) * width)

            # if no with or height has yet been set, clone the
            # original image's size
            if width <= 0:
                width = image_width

            if height <= 0:
                height = image_height

            # center image
            pos = (
                self.assigned_width / 2 - width / 2,
                self.assigned_height / 2 - height / 2
            )

            pos = (
                pos[0] if pos[0] >= 0 else 0,
                pos[1] if pos[1] >= 0 else 0
            )

            # resize image
            tmp_image = self._image.resize((width, height))

            # add round edges
            tmp_image = add_corners(
                tmp_image,
                current_style.borderTopLeftRadius,
                current_style.borderTopRightRadius,
                current_style.borderBottomLeftRadius,
                current_style.borderBottomRightRadius
            )

            # convert to pygame image
            now_image = pil_image_to_surface(tmp_image)

            # draw image to surface
            _surface.blit(now_image, pos)

        if current_style.borderWidth > 0:
            # print(f"drawing border, {current_style.borderColor}")
            pg.draw.rect(
                _surface,
                current_style.borderColor.irgba,
                r_rect,
                width=current_style.borderWidth,
                border_top_left_radius=current_style.borderTopLeftRadius,
                border_top_right_radius=current_style.borderTopRightRadius,
                border_bottom_left_radius=current_style.borderBottomLeftRadius,
                border_bottom_right_radius=current_style.borderBottomRightRadius
            )

        # draw children
        for child, params in self._child_params:
            child.draw(_surface)

        # draw children to surface
        surface.blit(_surface, (self._x, self._y))

        # draw wireframe
        if self.show_wireframe:
            # font for debugging
            font = pg.font.SysFont(None, 20)
            t = font.render(self.__class__.__name__, True, (255, 0, 0))
            surface.blit(t, (self._x, self._y - t.get_height()))

            if self._last_rows is not ...:
                for row in self._last_rows:
                    pg.draw.line(
                        surface,
                        (255, 0, 0, 100),
                        (self._x, self._y + row["y_start"]),
                        (self._x + width, self._y + row["y_start"])
                    )
                    pg.draw.line(
                        surface,
                        (255, 0, 0, 100),
                        (self._x, self._y + row["y_start"] + row["height"]),
                        (self._x + width, self._y + row["y_start"] + row["height"])
                    )

            if self._last_columns is not ...:
                for column in self._last_columns:
                    pg.draw.line(
                        surface,
                        (255, 0, 0, 100),
                        (self._x + column["x_start"], self._y),
                        (self._x + column["x_start"], self._y + height)
                    )
                    pg.draw.line(
                        surface,
                        (255, 0, 0, 100),
                        (self._x + column["x_start"] + column["width"], self._y),
                        (self._x + column["x_start"] + column["width"], self._y + height)
                    )

            # draw a different colored rectangle around the frame
            is_debug = hasattr(self, "debug_this")
            col = (255, 255 * (not is_debug), 255 * is_debug)
            pg.draw.rect(
                surface,
                col,
                pg.Rect(
                    (self._x, self._y),
                    (width, height)
                ),
                1
            )

            # display width if debug_this is enabled
            if is_debug:
                w_text = font.render(str(width), True, col)
                surface.blit(
                    w_text,
                    (
                        (self._x + width / 2) - w_text.get_width() / 2,
                        self._y
                    )
                )

        if requires_recalc:
            self.root.notify(GeoNotes.RequireRecalc)

    def place(
            self,
            x: int,
            y: int,
    ) -> None:
        """
        place the frame in a parent container

        :param x: x-position
        :param y: y-position
        """
        if not self.parent.check_set_layout(Layout.Absolute):
            raise TypeError(
                "can't place in a container that is"
                "not managed by \"Absolute\""
            )

        self.parent.set_layout(Layout.Absolute)

        self.__parent.add_child(self, x=x, y=y)

    def pack(
            self,
            anchor: tp.Literal["top", "bottom", "left", "right"] = TOP,
    ) -> None:
        """
        pack the frame into a parent container

        :param anchor: where to orient the frame at (direction)
        """
        if not self.parent.check_set_layout(Layout.Pack):
            raise TypeError(
                "can't pack in a container that is not managed by \"Pack\"."
                f" Configured Manager: {self.__parent.layout}"
            )

        self.parent.set_layout(Layout.Pack)

        self.__parent.add_child(self, anchor=anchor.lower())

    def grid(
            self,
            row: int,
            column: int,
            rowspan: int = 1,
            columnspan: int = 1,
            sticky: str = "",
            margin: int = 0,
    ) -> None:
        """
        grid the frame into a parent container

        :param row: the row the item should be placed in
        :param column: the column the item should be placed in
        :param rowspan: how many rows the widget should occupy
        :param columnspan: how many columns the widget should occupy
        :param sticky: expansion, can be a combination of "n", "e", "s", "w"
        :param margin: the distance to the grids borders
        """
        if not self.parent.check_set_layout(Layout.Grid):
            raise TypeError(
                "can't grid in a container that is not managed by \"Grid\""
            )

        self.parent.set_layout(Layout.Grid)

        self.__parent.add_child(
            self,
            row=row,
            column=column,
            sticky=sticky,
            margin=margin,
            rowspan=rowspan,
            columnspan=columnspan
        )

    def set_position(self, x: int, y: int) -> None:
        """
        set the child's position (used by parents)
        """
        self._x = x
        self._y = y

    def set_size(self, width: float, height: float) -> None:
        """
        set the child's size (used by parens)
        """
        self.width = width
        self.height = height

    def bind(
            self,
            sequence: FrameBind,
            func: tp.Callable[[tp.Any], tp.Any | None] = ...,
            add: tp.Literal["", "-"] | bool | None = ...
    ) -> int:
        """
        bind a callback to an event

        :param sequence: the event to listen for
        :param func: the function callback
        :param add: in case you want multiple callbacks for one event
        :returns: function id (for unbinding)
        """
        # if add isn't specified, remove all already existing binds
        if not add or add != "+":
            for b in self._binds.copy():
                if b["event"] == sequence:
                    self._binds.remove(b)

        new_id = 0
        if self._binds:
            new_id = max([e["id"] for e in self._binds]) + 1

        self._binds.append({
            "id": new_id,
            "event": sequence,
            "function": func
        })

        return new_id

    def unbind(self, func_id: int) -> None:
        """
        removes a bind event
        """
        for bind in self._binds:
            if bind["id"] == func_id:
                self._binds.remove(bind)
                return

    def _execute_event(self, event: FrameBind, *args, **kwargs) -> None:
        """
        check if a bind exists for the given event and if one does,
        execute it with the given parameters
        """
        for b in self._binds:
            if b["event"].value == event.value:
                b["function"](*args, **kwargs)

    def _on_hover(self) -> None:
        """
        called on hover
        """
        self._execute_event(FrameBind.hover)

        self.root.notify(GeoNotes.RequireRecalc)

    def _on_active(self) -> None:
        """
        called on active
        """
        self.root.set_focus(self)
        self._execute_event(FrameBind.active)

        self.root.notify(GeoNotes.RequireRecalc)

    def _on_no_active_hover(
            self,
            from_active: bool = False,
            from_hover: bool = False
    ) -> None:
        """
        called on no active / hover
        """
        if from_active:
            self._execute_event(FrameBind.active_release)

        if from_hover:
            self._execute_event(FrameBind.hover_release)

            self.root.notify(GeoNotes.RequireRecalc)

    def delete(self) -> None:
        """
        delete the widget
        """
        self.__parent = ...

        # terminate all children
        for child in self._children:
            child.delete()

"""
_entry.py
22. February 2023

A generic entry for entering text

Author:
Nilusink
"""
from ..types import (
    GeoNotes, KeyboardNotifyEvent, FrameBind, StringVar, Scheme, Style, Color,
)
from ..theme import ThemeManager
from contextlib import suppress
from ._label import Label
from ._frame import Frame
import typing as tp
import pygame as pg
import time


class Entry(Frame):
    """
    a generic entry for entering text
    """
    _label: Label = ...
    _string_var: StringVar = ...
    _placeholder_text: str = ...
    _placeholder_color: Color = ...
    _cursor_pos: int = 0
    _max_length: int | None = None
    _allowed: str = ...
    _scheme: Scheme
    _f_lower: bool = False
    _f_upper: bool = False

    def __init__(
            self,
            parent: tp.Union["Frame", tp.Any],
            width: int = ...,
            height: int = ...,
            border_width: int = ...,
            border_color: Color = ...,
            textvariable: StringVar = ...,
            placeholder_text: str = ...,
            placeholder_color: Color = ...,
            bg: Color = ...,
            fg: Color = ...,
            valid_symbols: str = ...,
            scheme: Scheme = ...,
            force_uppercase: bool = False,
            force_lowercase: bool = False,
            max_length: int | None = None,
            **kwargs
    ) -> None:
        """
        A widget where you can enter text

        :param valid_symbols: if given, the entry only allows the given
        characters. If scheme is given, this option will be ignored
        """
        self._f_lower = force_lowercase
        self._f_upper = force_uppercase
        self._max_length = max_length
        self._allowed = valid_symbols
        self._scheme = scheme

        if placeholder_text is ...:
            placeholder_text = "Entry"

        if placeholder_color is ...:
            placeholder_color = Color.from_hex("#666")

        self._placeholder_text = placeholder_text
        self._placeholder_color = placeholder_color

        # initialize text-variable
        self._string_var = textvariable
        if textvariable is ...:
            self._string_var = StringVar(value="")

        # set theme colors
        if bg is ... and "bg" in parent.theme.entry:
            bg = parent.theme.entry.bg

        if fg is ... and "fg" in parent.theme.entry:
            fg = parent.theme.entry.fg

        if border_width is ... and "border_width" in parent.theme.entry:
            border_width = parent.theme.entry.border_width

        if border_color is ... and "border_color" in parent.theme.entry:
            border_color = parent.theme.entry.border_color

        hover_border_color = ...
        active_border_color = ...
        if "hover_border_color" in parent.theme.entry:
            hover_border_color = parent.theme.entry.hover_border_color

        if "active_border_color" in parent.theme.entry:
            active_border_color = parent.theme.entry.active_border_color

        if "style" in kwargs:
            if kwargs["style"].backgroundColor is ...:
                kwargs["style"].backgroundColor = bg

            if kwargs["style"].color is ...:
                kwargs["style"].color = fg

            if kwargs["style"].border_width is ...:
                kwargs["style"].border_width = border_width

            if kwargs["style"].borderColor is ...:
                kwargs["style"].borderColor = border_color

        # create hover and active style if they don't exist in kwargs
        if "hover_style" not in kwargs:
            kwargs["hover_style"] = Style()

        if "active_style" not in kwargs:
            kwargs["active_style"] = Style()

        # apply default arguments
        if kwargs["hover_style"].borderColor is ...:
            kwargs["hover_style"].borderColor = hover_border_color

        if kwargs["active_style"].borderColor is ...:
            kwargs["active_style"].borderColor = active_border_color

        super().__init__(
            parent=parent,
            width=width,
            height=height,
            border_width=border_width,
            border_color=border_color,
            bg=bg,
            min_width=100,
            min_height=10,
            **kwargs
        )
        self.style.color = fg

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._label = Label(
            parent=self,
            text=""
        )
        self._label.grid(0, 0, sticky="nsew")

        self._sync_label_style("color", "normal")
        self._sync_label_style("color", "hover")
        self._sync_label_style("color", "active")

        self.style.notify_on(
            "color", lambda *_: self._sync_label_style("color")
        )
        self.hover_style.notify_on(
            "color", lambda *_: self._sync_label_style("color", "hover")
        )
        self.active_style.notify_on(
            "color", lambda *_: self._sync_label_style("color", "active")
        )

    def _sync_label_style(
            self, key: str,
            style_type: tp.Literal["normal", "hover", "active"] = "normal"
    ) -> None:
        """
        sync a label style with the button style
        """
        if style_type == "normal":
            self._label.style[key] = self.style[key]

        elif style_type == "hover":
            self._label.hover_style[key] = self.hover_style[key]

        elif style_type == "active":
            self._label.active_style[key] = self.active_style[key]

        else:
            raise ValueError("Invalid label sync type: ", style_type)

    # focus stuff
    def _on_hover(self) -> None:
        """
        change mouse
        """
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_IBEAM)
        super()._on_hover()

    def _on_no_active_hover(
            self,
            from_active: bool = False,
            from_hover: bool = False
    ) -> None:
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)

        super()._on_no_active_hover(from_active, from_hover)

    def stop_focus(self) -> None:
        """
        called when the entry is unfocused
        """
        self._on_no_active_hover(True, False)
        super().stop_focus()

    def draw(self, surface: pg.Surface) -> None:
        """
        insert cursor if active
        """
        self._is_active = self.focused
        bg_width, bg_height = self._label.get_size()

        current_style = self.style

        if self.is_hover:
            current_style = self.style.overwrite(self.hover_style)

        if self.is_active:
            current_style = self.style.overwrite(self.hover_style).overwrite(
                self.active_style
            )

        # set the label color to placeholder_color if no text has been entered
        is_placeholder = not self._string_var.get()
        if is_placeholder:
            self._label.text_variable.set(self._placeholder_text)
            self._label.style.color = self._placeholder_color

        else:
            self._label.text_variable.set(self._string_var.get())
            self._label.style.color = self.style.color

        super().draw(surface)

        # cursor only when active and blink
        if self.focused and int((2 * time.time()) % 2):
            # calculate cursor position
            x, y = self._label.get_position()
            width, height = self._label.text_size

            # get frame center
            center_x = self._x + x + bg_width / 2
            center_y = self._y + y + bg_height / 2

            cursor_text = self._label._font.render(
                self._string_var.get()[:self._cursor_pos],
                True,
                current_style.color.irgba
            )
            x_off = cursor_text.get_size()[0]

            # center label on frame center
            label_end = (
                center_x - (0 if is_placeholder else width / 2) + x_off,
                center_y - height / 2
            )

            pg.draw.rect(
                surface,
                current_style.color.irgb,
                pg.Rect(label_end, (3, height))
            )

    def notify(
            self,
            event: (
                    ThemeManager.NotifyEvent
                    | Style.NotifyEvent
                    | KeyboardNotifyEvent
            ),
            info: tp.Any = ...
    ) -> None:
        match event:
            case KeyboardNotifyEvent.key_down:
                if info.key == pg.K_BACKSPACE:
                    s_len = len(self._string_var.get())

                    # deletion if a scheme is given
                    if self._scheme is not ...:
                        if s_len > 0:
                            if self._cursor_pos < s_len:
                                # split string at the cursor and replace
                                # the next character with a space character
                                prev_string = self._string_var.get()
                                self._string_var.set(
                                    prev_string[
                                        :self._cursor_pos
                                    ]
                                    + " "
                                    + prev_string[self._cursor_pos + 1:]
                                )

                            else:
                                # split the string at the cursor and delete
                                # the next character
                                prev_string = self._string_var.get()
                                self._string_var.set(
                                    prev_string[
                                        :self._cursor_pos - 1
                                    ]
                                    + prev_string[self._cursor_pos:]
                                )

                                # de-increment cursor (if not already at 0)
                                if self._cursor_pos >= 0:
                                    self._cursor_pos -= 1

                        return

                    # normal deletion
                    if s_len > 0:
                        # split the string at the cursor and delete
                        # the next character
                        prev_string = self._string_var.get()
                        self._string_var.set(
                            prev_string[:self._cursor_pos-1]
                            + prev_string[self._cursor_pos:]
                        )

                        # de-increment cursor (if not already at 0)
                        if self._cursor_pos >= 0:
                            self._cursor_pos -= 1

                elif info.key == pg.K_RETURN:
                    self.root.set_focus(self.root)
                    self._execute_event(FrameBind.key_return)

                elif info.key == pg.K_LEFT:
                    if self._cursor_pos >= 0:
                        self._cursor_pos -= 1

                elif info.key == pg.K_RIGHT:
                    if self._cursor_pos < len(self._string_var.get()):
                        self._cursor_pos += 1

                # if none of the above apply and a unicode character is
                # present, add it to the string
                elif info.unicode:
                    override = False
                    set_character = None
                    next_valid = False

                    # force capitalize - lower the character
                    if self._f_upper:
                        info.unicode = info.unicode.upper()

                    if self._f_lower:
                        info.unicode = info.unicode.lower()

                    # check max length
                    if self._max_length is not None and\
                            self._cursor_pos >= self._max_length:
                        return

                    # check valid symbols
                    if self._allowed is not ... and\
                            info.unicode not in self._allowed\
                            and self._scheme is ...:
                        return

                    if self._scheme is not ...:
                        override = True
                        try:
                            # check current character
                            is_valid, punct = self._scheme.validate(
                                self._cursor_pos,
                                info.unicode
                            )

                            # check next character
                            with suppress(IndexError):
                                next_valid, _ = self._scheme.validate(
                                    self._cursor_pos + 1, info.unicode
                                )

                            if is_valid:
                                if punct is not None:
                                    set_character = punct

                            else:
                                return

                        except IndexError:
                            return

                    # insert character at cursor position
                    prev_string = self._string_var.get()
                    self._string_var.set(
                        prev_string[:self._cursor_pos]
                        + (set_character if set_character is not None else "")
                        + info.unicode
                        + prev_string[self._cursor_pos+override:]
                    )
                    self._cursor_pos += 1 + (
                            next_valid and set_character is not None
                    )

            case GeoNotes.SetActive:
                # new_index = self._label.get_index_on_position(
                #     info[0] - self._x
                # )
                #
                # if 0 <= new_index <= len(self._string_var.get()):
                #     self._cursor_pos = new_index
                #
                # print("index: ", new_index)

                self._cursor_pos = len(self._string_var.get())-1

                self.set_active()
                self.root.set_focus(self)

            case _:
                super().notify(event, info)


# TODO: clickable cursor
# TODO: enabled / disabled
# TODO: make a get_index_on_position function that doesn't crash the program
# TODO: not shown if no height | width | sticky is given

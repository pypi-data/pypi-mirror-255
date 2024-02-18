"""
_button.py
08. March 2023

Something you can click

Author:
Nilusink
"""
from ..types import Color, Layout, Style, Variable
from ..utils import arg_or_default
from ._label import Label
from ._frame import Frame
from copy import copy
import typing as tp


class Button(Frame):
    _label: Label = ...
    _command: tp.Callable[[], None] = ...
    _text_var: Variable = ...

    def __init__(
            self,
            parent: tp.Union["Frame", tp.Any],
            *,
            bg: Color = ...,
            fg: Color = ...,
            text: str = "Button",
            width: int = ...,
            height: int = ...,
            command: tp.Callable[[], None] = ...,
            textvariable: Variable = ...,
            **kwargs
    ) -> None:
        """

        """
        self._command = command
        self._text_var = textvariable

        # set theme colors
        if bg is ... and "bg" in parent.theme.button:
            bg = parent.theme.button.bg

        if fg is ... and "fg" in parent.theme.button:
            fg = parent.theme.button.fg

        hover_bg = hover_fg = ...
        active_bg = active_fg = ...
        if "hover_bg" in parent.theme.button:
            hover_bg = parent.theme.button.hover_bg

        if "hover_fg" in parent.theme.button:
            hover_fg = parent.theme.button.hover_fg

        if "active_bg" in parent.theme.button:
            active_bg = parent.theme.button.active_bg

        if "active_fg" in parent.theme.button:
            active_fg = parent.theme.button.active_fg

        if "style" in kwargs:
            if kwargs["style"].backgroundColor is ...:
                kwargs["style"].backgroundColor = bg

            if kwargs["style"].color is ...:
                kwargs["style"].color = fg

        # create hover and active style if they don't exist in kwargs
        if "hover_style" not in kwargs:
            kwargs["hover_style"] = Style()

        if "active_style" not in kwargs:
            kwargs["active_style"] = Style()

        # apply default arguments
        if kwargs["hover_style"].backgroundColor is ...:
            kwargs["hover_style"].backgroundColor = hover_bg

        if kwargs["hover_style"].color is ...:
            kwargs["hover_style"].color = hover_fg

        if kwargs["active_style"].backgroundColor is ...:
            kwargs["active_style"].backgroundColor = active_bg

        if kwargs["active_style"].color is ...:
            kwargs["active_style"].color = active_fg

        # initialize parent
        super().__init__(
            parent=parent,
            width=width,
            height=height,
            bg=bg,
            min_width=20,
            min_height=20,
            **kwargs
        )
        self.set_layout(Layout.Grid)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.style.color = arg_or_default(fg, Color.white(), ...)

        label_hover: Style = copy(kwargs["hover_style"])
        label_active: Style = copy(kwargs["active_style"])
        label_hover.backgroundColor = Color.transparent()
        label_active.backgroundColor = Color.transparent()

        self._label = Label(
            parent=self,
            text=text,
            textvariable=textvariable,
            fg=fg,
            style=Style(backgroundColor=Color.transparent()),
            hover_style=label_hover,
            active_style=label_active
        )
        self._label.grid(row=0, column=0, sticky="nsew")

        # first time style sync
        self._sync_label_style("color", "normal")

    def draw(self, surface) -> None:
        super().draw(surface)

    def _sync_label_style(
            self,
            key: str,
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

    def _on_hover(self) -> None:
        """
        set the label to hover
        """
        self._label.set_hover(False)

        super()._on_hover()

    def _on_active(self) -> None:
        """
        set the label to active
        """
        self._label.set_active(False)

        # execute assigned command
        if self._command is not ...:
            self._command()

        super()._on_active()

    def _on_no_active_hover(
            self,
            from_active: bool = False,
            from_hover: bool = False
    ) -> None:
        """
        set the label to no active-hover
        """
        self._label.set_no_hover_active(False)

        super()._on_no_active_hover(from_active, from_hover)

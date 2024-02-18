"""
_geo_manager.py
04. February 2023

How children are placed

Author:
Nilusink
"""
from ..types import Layout, BetterDict, TOP, BOTTOM, LEFT, RIGHT, GeoNotes
from ._supports_children import SupportsChildren
from ..utils import point_in_box
from copy import deepcopy
import typing as tp
import pygame as pg


if tp.TYPE_CHECKING:
    from ._frame import Frame


class GeometryManager(SupportsChildren):
    """
    Manages how children are placed inside a parent container
    """
    _layout: Layout = Layout.Absolute
    _width: float = 0   # -1 means not configured -> takes minimum size
    # required by its children
    _height: float = 0  # or the size it gets by the parents geometry manager
    assigned_width: float = 0
    assigned_height: float = 0
    _width_configured: bool = False
    _height_configured: bool = False
    _child_params: list[tuple[tp.Any, BetterDict]] = ...
    layout_params: BetterDict = ...
    _grid_params: BetterDict = ...

    _child_override: bool = False
    _is_active: bool = False
    _is_hover: bool = False

    _last_rows: list[dict[
        str,
        list[tuple[tp.Any, BetterDict, bool]] | float
    ]] = ...
    _last_columns: list[dict[
        str,
        list[tuple[tp.Any, BetterDict, bool]] | float
    ]] = ...

    def __init__(
            self,
            layout: Layout = ...,
            margin: int = 0,
            padding: int = 0
    ):
        super().__init__()

        if layout is not ...:
            if layout not in (Layout.Grid, Layout.Pack, Layout.Absolute):
                raise ValueError(f"Invalid layout type: {layout}")

        self._layout = Layout.Absolute if layout is ... else layout
        self.layout_params = BetterDict({
            "margin": margin,
            "padding": padding
        })
        self._child_params = []
        self._grid_params = BetterDict({
            "rows": {},
            "columns": {}
        })

    @property
    def layout(self) -> Layout:
        """
        the containers layout type
        """
        return self._layout

    @property
    def width(self) -> float:
        return self._width
    
    @width.setter
    def width(self, value: float) -> None:
        self._width = value
        self._width_configured = True

    def unset_width(self) -> None:
        """
        act as if the width has never been set
        """
        self._width_configured = False

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        self._height = value
        self._height_configured = True

    def unset_height(self) -> None:
        """
        act as if the height has never been set
        """
        self._height_configured = False

    @property
    def is_hover(self) -> bool:
        return self._is_hover

    @property
    def is_active(self) -> bool:
        return self._is_active

    def set_focus(self, widget: tp.Union["GeometryManager", None]):
        """
        set this item as currently focused
        """

    def stop_focus(self):
        """
        remove focus from this item
        """

    def _on_active(self) -> None:
        """
        called when button is clicked
        not implemented by default
        """

    def _on_hover(self) -> None:
        """
        called on hover
        not implemented by default
        """

    def _on_no_active_hover(
            self,
            from_active: bool = False,
            from_hover: bool = False
    ) -> None:
        """
        called when either hover or active goes back to normal
        not implemented by default
        """

    def set_active(self, override: bool = False) -> None:
        """
        change the widget to an active state
        """
        if not self._child_override:
            if not self._is_active:  # only call on new event
                self._on_active()

            self._is_hover = False
            self._is_active = True

        self._child_override = self._child_override or override

    def set_hover(self, override: bool = False) -> None:
        """
        set the widget to a hover state
        """
        if not self._child_override:
            if not self._is_hover:  # only call on new event
                self._on_hover()

            self._is_hover = True
            self._is_active = False

        self._child_override = self._child_override or override

    def set_no_hover_active(self, override: bool = False) -> None:
        """
        set the widget to "normal" mode
        """
        if not self._child_override:
            if self._is_hover or self._is_active:  # only call no new event
                self._on_no_active_hover(self._is_active, self._is_hover)

            self._is_hover = False
            self._is_active = False

        self._child_override = self._child_override or override

    def _notify_child_active_hover(self, mouse_pos: tuple[int, int]) -> bool:
        has_hit: bool = False

        for child in self._children:
            child: Frame

            pos = child.get_position()
            size = child.get_size()

            # noinspection PyTypeChecker
            if point_in_box(mouse_pos, (*pos, *size)):
                has_hit = True
                child.notify(
                    GeoNotes.SetActive if pg.mouse.get_pressed(3)[0]
                    else GeoNotes.SetHover,
                    (mouse_pos[0] - pos[0], mouse_pos[1] - pos[1])
                )
                continue

            child.notify(GeoNotes.SetNormal)

        return has_hit

    def notify(self, event, info) -> None:
        """
        for notifications from child / parent classes
        """
        self._child_override = False
        match event:
            case GeoNotes.SetHover:
                if self._notify_child_active_hover(info):
                    self.set_no_hover_active()
                else:
                    self.set_hover()

            case GeoNotes.SetActive:
                if self._notify_child_active_hover(info):
                    self.set_no_hover_active()
                else:
                    self.set_active()

            case GeoNotes.SetNormal:
                # also set children to inactive
                self._notify_child_active_hover((-1, -1))

                self.set_no_hover_active()

    # layout configuration
    def set_layout(self, layout: Layout) -> None:
        """
        set the container's layout type
        """
        if layout not in Layout:
            raise ValueError("Invalid container layout: ", layout)

        if self._layout != layout:
            if len(self._child_params) > 0:
                # if children are already present, delete them
                for child, _param in self._child_params:
                    child.delete()

                self._child_params.clear()

                raise RuntimeWarning(
                    "changing layout with children already present!"
                )

            self._layout = layout

    def check_set_layout(self, layout: Layout) -> bool:
        """
        checks if the layout can be changed
        """
        # not a real layout type
        if layout not in Layout:
            return False

        # is already the same layout
        if self._layout == layout:
            return True

        # no children present - can be easily changed
        if len(self._children) == 0:
            return True

        return False

    def grid_columnconfigure(
            self,
            column: int | tp.Iterable[int],
            weight: float = 1
    ) -> None:
        """
        configure one or more grid columns
        """
        # if the column is given as a list,
        # call this function with an integer as parameter
        if isinstance(column, tp.Iterable):
            for c in column:
                self.grid_columnconfigure(c, weight=weight)

            return

        # check if the layout is "grid"
        if not self.check_set_layout(Layout.Grid):
            raise ValueError("Invalid geometry type for grid-configuration")

        self.set_layout(Layout.Grid)

        self._grid_params["columns"][column] = {
            "weight": weight
        }

    def grid_rowconfigure(
            self,
            row: int | tp.Iterable[int],
            weight: float = 1
    ) -> None:
        """
        configure one or more grid rows
        """
        # if the row is given a list, call this
        # function with an integer as parameter
        if isinstance(row, tp.Iterable):
            for r in row:
                self.grid_rowconfigure(r, weight=weight)

            return

        # check if the layout is "grid"
        if not self.check_set_layout(Layout.Grid):
            raise ValueError("Invalid geometry type for grid-configuration")

        self.set_layout(Layout.Grid)

        self._grid_params["rows"][row] = {
            "weight": weight
        }

    # other stuff
    def add_child(self, child: tp.Any, **params) -> None:
        """
        add a child to the collection
        """
        if child not in self._children:
            super().add_child(child)
            self._child_params.append((child, BetterDict(params)))

    def calculate_geometry(self):
        """
        calculate how each individual child should be placed
        """
        match self._layout:
            case Layout.Absolute:
                # since the positioning is absolute,
                # the children should not influence the parents size
                for child, params in self._child_params:
                    child.set_position(params.x, params.y)

            case Layout.Pack:
                directional_dict: dict[str, int | list] = {
                    "total_x": 0,
                    "total_y": 0,
                    "children": [],
                    "sizes": []
                }
                top = deepcopy(directional_dict)
                bottom = deepcopy(directional_dict)
                left = deepcopy(directional_dict)
                right = deepcopy(directional_dict)

                # get all sizes and group by anchor
                for child, param in self._child_params:
                    child_size = child.calculate_size()

                    if param.anchor == TOP:
                        top["children"].append(child)
                        top["sizes"].append(child_size)
                        top["total_x"] += child_size[0]
                        top["total_y"] += child_size[1]

                    elif param.anchor == BOTTOM:
                        bottom["children"].append(child)
                        bottom["sizes"].append(child_size)
                        bottom["total_x"] += child_size[0]
                        bottom["total_y"] += child_size[1]

                    elif param.anchor == LEFT:
                        left["children"].append(child)
                        left["sizes"].append(child_size)
                        left["total_x"] += child_size[0]
                        left["total_y"] += child_size[1]

                    elif param.anchor == RIGHT:
                        right["children"].append(child)
                        right["sizes"].append(child_size)
                        right["total_x"] += child_size[0]
                        right["total_y"] += child_size[1]

                top["total_y"] += self.layout_params.padding * len(
                    top["children"]
                ) - 1
                bottom["total_y"] += self.layout_params.padding * len(
                    bottom["children"]
                ) - 1

                left["total_x"] += self.layout_params.padding * len(
                    left["children"]
                ) - 1
                right["total_x"] += self.layout_params.padding * len(
                    right["children"]
                ) - 1

                # if not configured, set own size
                total_x = max([top["total_x"], bottom["total_x"],
                               left["total_x"] + right["total_x"]])
                total_y = max([left["total_y"], right["total_y"],
                               top["total_y"] + bottom["total_y"]])

                # add margin
                total_x += self.layout_params.margin * 2
                total_y += self.layout_params.margin * 2

                if not self._width_configured:
                    self._width = total_x

                    if hasattr(self, "debug_this"):
                        print("setting width: ", total_x)

                else:
                    total_x = self._width
    
                if not self._height_configured:
                    if hasattr(self, "debug_this"):
                        print("setting height: ", total_y)

                    self._height = total_y

                else:
                    total_y = self.height

                # tell the children where they should be
                y_cen = total_y / 2
                x_cen = total_x / 2

                # left
                x_now = self.layout_params.margin
                for child, size in zip(left["children"], left["sizes"]):
                    child.set_position(x_now, y_cen - size[1] / 2)
                    x_now += size[0] + self.layout_params.padding

                # right
                x_now = total_x - self.layout_params.margin
                for child, size in zip(right["children"], right["sizes"]):
                    child.set_position(x_now - size[0], y_cen - size[1] / 2)
                    x_now -= size[0] + self.layout_params.padding

                # top
                y_now = self.layout_params.margin
                for child, size in zip(top["children"], top["sizes"]):
                    child.set_position(x_cen - size[0] / 2, y_now)
                    y_now += size[1] + self.layout_params.padding

                # bottom
                y_now = total_y - self.layout_params.margin
                for child, size in zip(bottom["children"], bottom["sizes"]):
                    child.set_position(x_cen - size[0] / 2, y_now - size[1])
                    y_now -= size[1] + self.layout_params.padding

            case Layout.Grid:
                rows: list[dict[
                    str,
                    list[tuple[tp.Any, BetterDict, bool]] | float
                ]] = []
                columns: list[dict[
                    str,
                    list[tuple[tp.Any, BetterDict, bool]] | float
                ]] = []

                for child, params in self._child_params:
                    row, column = params["row"], params["column"]

                    # if row was not yet made, make all previous ones
                    min_rows = row + params.rowspan - 1
                    min_columns = column + params.columnspan - 1

                    if len(rows) <= min_rows:
                        for n_row in range(len(rows), min_rows+1):
                            out = {
                                "weight": 0,
                                "children": []
                            }

                            if n_row in self._grid_params.rows:
                                config = self._grid_params.rows[n_row]

                                if "weight" in config:
                                    out["weight"] = config["weight"]

                            rows.append(out)

                    if len(columns) <= min_columns:
                        for n_col in range(len(columns), min_columns+1):
                            out = {
                                "weight": 0,
                                "children": []
                            }

                            if n_col in self._grid_params.columns:
                                config = self._grid_params.columns[n_col]

                                if "weight" in config:
                                    out["weight"] = config["weight"]

                            columns.append(out)

                    rows[row]["children"].append((child, params, True))
                    
                    # if rowspan is given, also add the widget to all the
                    # corresponding other rows
                    if "rowspan" in params:
                        for row_incrementor in range(1, params.rowspan):
                            rows[row + row_incrementor]["children"]\
                                .append(
                                (child, params, False)
                            )

                    columns[column]["children"].append((child, params, True))

                    if "columnspan" in params:
                        for column_incrementor in range(1, params.columnspan):
                            columns[column + column_incrementor]["children"]\
                                .append(
                                (child, params, False)
                            )

                matrix: list[list] = []

                # append all the children to a 2d matrix and check if one
                # cell has multiple children
                for r in range(len(rows)):
                    matrix.append([])

                    for c in range(len(columns)):
                        child = [
                            chi for chi in rows[r]["children"]
                            if chi in columns[c]["children"]
                        ]
                        child = list(child)

                        if len(child) > 1:
                            raise ValueError(
                                f"{len(child)} children assigned "
                                f"to row {r} column {c}!"
                            )

                        if child:
                            matrix[r].append(child[0])

                        else:
                            matrix[r].append(...)

                # calculate the minimal size for each row
                for r, row in enumerate(rows):
                    rows[r]["max_size"] = 0

                    for child, params, _is_widget in row["children"]:
                        child.calculate_size()
                        _, y = child.get_size()

                        y += 2 * params.margin

                        # split size between rows
                        y /= params.rowspan

                        if y > rows[r]["max_size"]:
                            rows[r]["max_size"] = y

                # calculate the minimal size for each column
                for c, column in enumerate(columns):
                    columns[c]["max_size"] = 0

                    for child, params, _is_widget in column["children"]:
                        child.calculate_size()
                        x, _ = child.get_size()

                        x += 2 * params.margin

                        # split size between columns
                        x /= params.columnspan

                        if x > columns[c]["max_size"]:
                            columns[c]["max_size"] = x

                # calculate the container size
                columns_width, rows_height = self.assigned_width, self.assigned_height

                # only subtract rows that don't have a weight
                min_width = sum([c["max_size"] for c in columns])
                min_height = sum([r["max_size"] for r in rows])

                # if children exist, set min size
                if len(columns) + len(rows) > 0:
                    if columns_width == 0 or rows_height == 0 and not\
                            self._width_configured:

                        # only set if child requires greater width
                        if min_width > self._width:
                            if hasattr(self, "debug_this"):
                                print(
                                    "setting width (children min): ", min_width
                                    )
                            self._width = min_width

                    if columns_width == 0\
                            or rows_height == 0\
                            and not self._height_configured:

                        # only set if child requires greater height
                        if min_height > self._height:
                            if hasattr(self, "debug_this"):
                                print(
                                    "setting height (children min): ",
                                    min_height
                                    )
                            self._height = min_height

                # if a size has been set by the user, overwrite the calculated
                # size
                if self._width_configured:
                    columns_width = self._width

                if self._height_configured:
                    rows_height = self.height

                # assign extra space
                extra_width = columns_width - sum(
                    [c["max_size"] for c in columns if c["weight"] == 0]
                )
                extra_height = rows_height - sum(
                    [r["max_size"] for r in rows if r["weight"] == 0]
                )

                total_row_weight = sum(
                    [row["weight"] for row in rows]
                )
                total_column_weight = sum(
                    [column["weight"] for column in columns]
                )

                # assign each row and column a specific size
                for r in range(len(rows)):
                    if total_row_weight == 0:
                        rows[r]["height"] = 0

                    else:
                        # assign either the minimum size or the
                        # calculated dynamic one
                        w_size = (
                            (rows[r]["weight"] / total_row_weight)
                            * extra_height
                        ).__floor__()
                        rows[r]["height"] = w_size

                    rows[r]["y_start"] = self.layout_params.padding / 2 + sum(
                        [prev_row["height"] for prev_row in rows[:r]]
                    )

                for c in range(len(columns)):
                    if total_column_weight == 0:
                        columns[c]["width"] = 0

                    else:
                        # assign either the minimum size or the
                        # calculated dynamic one
                        w_size = (
                            (
                                columns[c]["weight"]
                                / total_column_weight
                            )
                            * extra_width
                        ).__floor__()
                        columns[c]["width"] = w_size

                    columns[c]["x_start"] = self.layout_params.padding / 2\
                        + sum(
                        [prev_col["width"] for prev_col in columns[:c]]
                    )

                if hasattr(self, "debug_this"):
                    print(self.width, extra_width, min_width)
                    print([f"width: {c['width']}" for c in columns])

                # place children
                for child, params in self._child_params:
                    # place the child proportional to the table and stickiness
                    # size = list(child.calculate_size())
                    size = [child._width, child._height]

                    row, column = params.row, params.column
                    sticky = params.sticky
                    margin = params.margin

                    columns_width = sum([
                        columns[c]["width"] for c in
                        range(column, column + params.columnspan)
                    ])
                    rows_height = sum([
                        rows[r]["height"] for r in
                        range(row, row + params.rowspan)
                    ])

                    x = columns[column]["x_start"]
                    y = rows[row]["y_start"]

                    x_diff = columns_width - size[0]
                    y_diff = rows_height - size[1]

                    # offsets for width / height configured
                    x_position_offset = 0
                    y_position_offset = 0

                    if hasattr(self, "debug_this"):
                        print("cw: ", columns_width, params.columnspan)

                    # assign stickiness
                    if not child._width_configured:
                        if "w" in sticky and "e" in sticky:
                            # sticky on both sides, expand to fit the box
                            size[0] += x_diff - 2 * params.margin

                        elif "w" in sticky:
                            # sticky only west, anchor left
                            x_position_offset = 0

                        elif "e" in sticky:
                            # sticky only east, anchor right
                            x_position_offset = x_diff - params.margin

                        else:
                            # no sticky set, center on x
                            x_position_offset += x_diff / 2 - params.margin

                        child.assigned_width = size[0]

                    else:
                        # if width is configured, center the widget based
                        # on its configured width
                        x_position_offset += x_diff / 2 - params.margin

                    if not child._height_configured:
                        if "n" in sticky and "s" in sticky:
                            # sticky on both sides, expand to fit the box
                            size[1] += y_diff - 2 * params.margin

                        elif "n" in sticky:
                            # sticky only north, anchor the widget upwards
                            y_position_offset = 0

                        elif "s" in sticky:
                            # sticky only south, anchor the widget downwards
                            y_position_offset = y_diff - params.margin

                        else:
                            # no sticky set, center on y
                            y_position_offset += y_diff / 2 - params.margin

                        child.assigned_height = size[1]

                    else:
                        # if height is configured, center the widget based
                        # on its configured height
                        y_position_offset += y_diff / 2 - params.margin

                    child.set_position(
                        x + margin + max([x_position_offset, 0]),
                        y + margin + max([y_position_offset, 0])
                    )

                self._last_rows = rows
                self._last_columns = columns

            case _:
                raise ValueError(f"Invalid geometry type: {self._layout}")

    def calculate_size(self) -> tuple[int, int]:
        """
        calculate how big the container should be
        """
        # make sure the geometry is up-to-date
        self.calculate_geometry()

        width = self._width
        height = self._height

        width = round(width)
        height = round(height)

        return width, height

"""
_color.py
04. February 2023

a color class

Author:
Nilusink
"""
import typing as tp


class Color:
    _rgb: tuple[float, float, float] = ...
    _alpha: float = 255
    _hex: str = ...

    def __init__(self) -> None:
        self.rgb = 0, 0, 0, 0

    # constructors
    @classmethod
    def from_rgb(
            cls,
            red: float,
            green: float,
            blue: float,
            alpha: float = ...
    ) -> "Color":
        new = cls()
        new.rgb = [red, green, blue] + ([255] if alpha is ... else [alpha])

        return new

    @classmethod
    def from_hex(cls, hex_value: str, alpha: float = ...) -> "Color":
        new = cls()
        new.hex = hex_value
        new.alpha = 255 if alpha is ... else alpha

        return new

    @classmethod
    def transparent(cls) -> "Color":
        """
        a fully transparent color
        """
        return cls.from_rgb(0, 0, 0, 0)

    @classmethod
    def white(cls) -> "Color":
        """
        white
        """
        return cls.from_hex("#fff")

    @classmethod
    def black(cls) -> "Color":
        """
        black
        """
        return cls.from_hex("#000")

    # properties
    @property
    def r(self) -> float:
        return self._rgb[0]

    @property
    def g(self) -> float:
        return self._rgb[1]

    @property
    def b(self) -> float:
        return self._rgb[2]

    @property
    def rgb(self) -> tuple[float, float, float]:
        return self._rgb

    @property
    def irgb(self) -> tuple[int, int, int]:
        return (
            int(self.r),
            int(self.g),
            int(self.b)
        )

    @property
    def rgba(self) -> tuple[float, float, float, float]:
        return tuple(self._rgb) + (self._alpha,)

    @rgb.setter
    def rgb(
            self,
            value: tuple[float, float, float]
            | tuple[float, float, float, float]
    ) -> None:
        if len(value) == 4:
            *self._rgb, self._alpha = value

        elif len(value) == 3:
            self._rgb = value

        else:
            raise ValueError(
                f"The rgb tuple must have a length"
                f"of either 3 or 4!  (not {len(value)})"
            )

        self._recalculate_colors("r")

    @property
    def irgba(self) -> tuple[int, int, int, int]:
        return (
            int(self.r),
            int(self.g),
            int(self.b),
            int(self._alpha)
        )

    @property
    def hex(self) -> str:
        return self._hex

    @hex.setter
    def hex(self, value: str) -> None:
        if len(value) == 3:  # ex: fff
            self._hex = "#" + 2*value[0] + 2*value[1] + 2*value[2]

        elif len(value) == 4:  # ex: #fff
            self._hex = "#" + 2*value[1] + 2*value[2] + 2*value[3]

        elif len(value) == 6:  # ex: ffffff
            self._hex = "#" + value

        elif len(value) == 7:  # ex: #ffffff
            self._hex = value

        else:
            raise ValueError(
                f"The hex string must be either 3, 4"
                f"or 6 or 7 characters long! (not {len(value)})"
            )

        self._recalculate_colors("h")

    @property
    def alpha(self) -> float:
        return self.alpha

    @alpha.setter
    def alpha(self, value: float) -> None:
        self._alpha = value

    # internal stuff
    def _recalculate_colors(
            self,
            calc_from: tp.Literal["r", "rgb", "h", "hex"]
    ):
        if calc_from in ("rgb", "r"):
            self._hex = f"#" \
                        f"{hex(self.rgb[0].__floor__())[2:]}" \
                        f"{hex(self.rgb[1].__floor__())[2:]}" \
                        f"{hex(self.rgb[2].__floor__())[2:]}".upper()

        elif calc_from in ("hex", "h"):
            r = self._hex[1:3]
            g = self._hex[3:5]
            b = self._hex[5:7]

            self._rgb = (
                int(r, 16),
                int(g, 16),
                int(b, 16)
            )

            self._hex.upper()

    # magic
    def __hex__(self) -> str:
        return self.hex

    def __repr__(self) -> str:
        return f"<{self.hex} - {self.rgb}>"

    def __str__(self) -> str:
        return self.__repr__()

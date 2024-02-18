"""
_scheme.py
26. May 2023

A scheme for text

Author:
Nilusink
"""
import typing as tp
import string


class Scheme:
    """
    a scheme for text
    """
    _current_scheme: list[str]

    def __init__(self) -> None:
        self._current_scheme = []

    @classmethod
    def from_string(cls, scheme: str) -> tp.Self:
        """
        create a scheme based on the string representation
        """
        # parse the scheme
        parsed_scheme = []
        i = 0
        while i < len(scheme):
            now = scheme[i]

            # if special, find back
            if now == "<" and scheme[i+1] == "|":
                additional = 2
                while i + additional + 1 < len(scheme):
                    if scheme[i + additional] == "|"\
                            and scheme[i + additional + 1] == ">":
                        break

                    i += 1

                else:
                    continue

                parsed_scheme.append(
                    f"<|{scheme[i+1:i+additional]}|>"
                )

                i += additional + 2
                continue

            parsed_scheme.append(now)
            i += 1

        new_instance = cls()
        new_instance._current_scheme = parsed_scheme

        return new_instance

    def get(self) -> str:
        return "".join(self._current_scheme)

    def any(self) -> tp.Self:
        self._current_scheme.append("x")
        return self

    def lowercase(self) -> tp.Self:
        """
        any ascii lowercase letters (abcdefghijklmnopqrstuvwxyz)
        """
        self._current_scheme.append("l")
        return self

    def l(self) -> tp.Self:
        """
        same as lowercase
        """
        return self.lowercase()

    def uppercase(self) -> tp.Self:
        """
        all ascii uppercase letters (ABCDEFGHIJKLMNOPQRSTUVWXYZ)
        """
        self._current_scheme.append("u")
        return self

    def u(self) -> tp.Self:
        """
        same as uppercase
        """
        return self.uppercase()

    def letters(self) -> tp.Self:
        """
        all ascii lowercase + uppercase letters
        (abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ)
        """
        self._current_scheme.append("a")
        return self

    def a(self) -> tp.Self:
        """
        same as letters
        """
        return self.letters()

    def digits(self) -> tp.Self:
        """
        all numbers from 0 to 10 (0123456789)
        """
        self._current_scheme.append("d")
        return self

    def d(self) -> tp.Self:
        """
        same as numbers
        """
        return self.digits()

    def hexdigits(self) -> tp.Self:
        """
        all hexadecimal digits (0123456789abcdefABCDEF)
        """
        self._current_scheme.append("h")
        return self

    def h(self) -> tp.Self:
        """
        same as hexdigits
        """
        return self.hexdigits()

    def octdigits(self) -> tp.Self:
        """
        all octal digits (01234567)
        """
        self._current_scheme.append("o")
        return self

    def o(self) -> tp.Self:
        """
        same as octdigits
        """
        return self.octdigits()

    def symbols(self) -> tp.Self:
        r"""
        all symbols (!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~)
        """
        self._current_scheme.append("s")
        return self

    def s(self) -> tp.Self:
        """
        same as symbols
        """
        return self.symbols()

    def printable(self) -> tp.Self:
        r"""
        all ascii printable characters
        (
        0123456789
        abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
        !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
         \t\n\r\v\f
         )
        """
        self._current_scheme.append("p")
        return self

    def p(self) -> tp.Self:
        """
        same as printable
        """
        return self.printable()

    def specific(self, character: str) -> tp.Self:
        """
        a specific string to be inserted in between
        """
        self._current_scheme.append(f"<|{character}|>")
        return self

    def validate(self, position: int, to_check: str) -> tuple[int, str | None]:
        """
        checks if the given character fits into the desired position
        """
        to_match = self._current_scheme[position]

        if to_match.startswith("<|") and to_match.endswith("|>"):
            return 2, to_match.lstrip("<|").rstrip("|>")

        match to_match:
            case "l":
                return int(to_check in string.ascii_lowercase), None

            case "u":
                return int(to_check in string.ascii_uppercase), None

            case "a":
                return int(to_check in string.ascii_letters), None

            case "d":
                return int(to_check in string.digits), None

            case "o":
                return int(to_check in string.octdigits), None

            case "h":
                return int(to_check in string.hexdigits), None

            case "s":
                return int(to_check in string.punctuation), None

            case "p":
                return int(to_check in string.printable), None

            case _:
                raise ValueError(f"Invalid scheme: {self.get()}")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.get()}>"

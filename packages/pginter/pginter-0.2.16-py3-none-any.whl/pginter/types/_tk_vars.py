"""
_tk_vars.py
15. May 2023

implements tkinter variables like StrVar and IntVar

Author:
Nilusink
"""
from copy import copy, deepcopy
from enum import Enum
import typing as tp


_T = tp.TypeVar("_T")


class _TraceModes(Enum):
    array = "array"
    read = "read"
    write = "write"
    unset = "unset"


class Variable:
    TraceModes = _TraceModes

    _master = ...
    _value: _T = ...
    _name: str = ...
    _deepcopy: bool = False

    _traces: list[tuple[
        _TraceModes | list[_TraceModes],
        tp.Callable[[tp.Self, int, _TraceModes], None]
    ]]

    def __init__(
            self,
            master=None,
            value: _T = None,
            name: str = None,
            use_deepcopy: bool = False
    ) -> None:
        self._traces = []

        self._master = master
        self._value = value
        self._name: str = name
        self._deepcopy = use_deepcopy

    def _check_send(self, mode: _TraceModes) -> None:
        """
        checks if a trace is set and if it is, send callback
        """
        for m, c in self._traces:
            if any([
                isinstance(m, list) and mode in m,
                m == mode
            ]):
                c(self, 0, mode)

    @property
    def name(self) -> str:
        return self._name

    def get(self) -> _T:
        """
        get the variable
        """
        self._check_send(_TraceModes.read)
        return deepcopy(self._value) if self._deepcopy else copy(self._value)

    def set(self, value: _T) -> None:
        """
        set the variable
        """
        self._value = value
        self._check_send(_TraceModes.write)

    def trace_add(
            self,
            mode: _TraceModes | list[_TraceModes],
            callback_name: tp.Callable[[tp.Self, int, _TraceModes], None]
    ) -> None:
        """
        create a trace
        """
        if mode == _TraceModes.array:
            raise RuntimeWarning("mode \"array\" is currently not implemented")

        # noinspection PyTypeChecker
        self._traces.append((mode, callback_name))

    def trace_remove(
            self,
            mode: _TraceModes | list[_TraceModes],
            callback_name: tp.Callable[[tp.Self, int, _TraceModes], None]
    ) -> None:
        """
        delete a trace
        """
        for i, (m, c) in enumerate(self._traces.copy()):
            if m == mode and c == callback_name:
                self._traces.pop(i)

    def trace_info(self) -> None:
        """
        trace infos
        """
        for m, c in enumerate(self._traces):
            print(f"{m}: {c}")

    def __iadd__(self, other: _T) -> tp.Self:
        self.set(self._value + other)
        return self

    def __isub__(self, other: _T) -> tp.Self:
        self.set(self._value - other)
        return self

    def __del__(self) -> None:
        """
        class delete
        """
        self._check_send(_TraceModes.unset)


# Actual TkVariables:
class StringVar(Variable):
    def __init__(
            self,
            master=None,
            value: str = None,
            name: str = None
    ) -> None:
        super().__init__(master, value, name)

    def set(self, value: str) -> None:
        super().set(value)

    def get(self) -> str:
        return super().get()


class IntVar(Variable):
    def __init__(
            self,
            master=None,
            value: int = None,
            name: str = None
    ) -> None:
        super().__init__(master, value, name)

    def set(self, value: int) -> None:
        super().set(value)

    def get(self) -> int:
        return super().get()


class DoubleVar(Variable):
    def __init__(
            self,
            master=None,
            value: float = None,
            name: str = None
    ) -> None:
        super().__init__(master, value, name)

    def set(self, value: float) -> None:
        super().set(value)

    def get(self) -> float:
        return super().get()


class BooleanVar(Variable):
    def __init__(
            self,
            master=None,
            value: bool = None,
            name: str = None
    ) -> None:
        super().__init__(master, value, name)

    def set(self, value: bool) -> None:
        super().set(value)

    def get(self) -> bool:
        return super().get()


from __future__ import annotations

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import sarus_init


class Slice(DataSpecWrapper[slice]):
    @sarus_init("std.SLICE")
    def __init__(self, *args, **kwargs) -> None:
        ...

    @classmethod
    def from_value(cls, value: slice) -> Slice:
        elems = [
            value.start,
            value.stop,
            value.step,
        ]
        return Slice(*elems)


class Set(DataSpecWrapper[set]):
    @sarus_init("std.SET")
    def __init__(self, *args, **kwargs) -> None:
        """Need to pass all arguments Set(*args)."""
        ...

    @classmethod
    def from_value(cls, value: set) -> Set:
        elems = [e for e in value]
        return Set(*elems)


class Dict(DataSpecWrapper[dict]):
    @sarus_init("std.DICT")
    def __init__(self, *args, **kwargs) -> None:
        """Need to pass all arguments Dict(**kwargs)."""
        ...

    @classmethod
    def from_value(cls, value: dict) -> Dict:
        elems = {k: v for k, v in value.items()}
        return Dict(**elems)


class List(DataSpecWrapper[list]):
    @sarus_init("std.LIST")
    def __init__(self, *args, **kwargs) -> None:
        """Need to pass all arguments List(*args)."""

    def __iter__(self):
        """The iterator protocol is emulated using __getitem__.

        X_train, X_test, y_train, y_test = train_test_split(...)

        Under the hood it does:
        result: DataSpecWrapper[List] = train_test_split(...)
        X_train = result.__getitem__[0]
        X_test = result.__getitem__[1]
        y_train = result.__getitem__[2]
        y_test = result.__getitem__[3]
        """
        self.__sarus_idx__ = 0
        return self

    def __next__(self):
        try:
            idx = self.__sarus_idx__
            self.__sarus_idx__ += 1
            return self[idx]
        except IndexError:
            raise StopIteration

    @classmethod
    def from_value(cls, value: list) -> List:
        elems = [e for e in value]
        return List(*elems)


class Tuple(DataSpecWrapper[tuple]):
    @sarus_init("std.TUPLE")
    def __init__(self, *args, **kwargs) -> None:
        """Need to pass all arguments Tuple(*args)."""

    # The iterator protocol is emulated using __getitem__
    def __iter__(self):
        self.__sarus_idx__ = 0
        return self

    def __next__(self):
        try:
            idx = self.__sarus_idx__
            self.__sarus_idx__ += 1
            return self[idx]
        except IndexError:
            raise StopIteration

    @classmethod
    def from_value(cls, value: tuple) -> Tuple:
        elems = [e for e in value]
        return Tuple(*elems)


class Int(DataSpecWrapper[int]):
    @sarus_init("std.INT")
    def __init__(self, *args, **kwargs) -> None:
        ...


class Float(DataSpecWrapper[float]):
    @sarus_init("std.FLOAT")
    def __init__(self, *args, **kwargs) -> None:
        ...


class String(DataSpecWrapper[str]):
    @sarus_init("std.STRING")
    def __init__(self, *args, **kwargs) -> None:
        ...


class Bool(DataSpecWrapper[bool]):
    @sarus_init("std.BOOL")
    def __init__(self, *args, **kwargs) -> None:
        ...

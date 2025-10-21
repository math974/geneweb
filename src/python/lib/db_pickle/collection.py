from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, Iterable, Optional, TypeVar

T = TypeVar("T")
U = TypeVar("U")


def make(*, length: int) -> list[Optional[T]]:
    """Create a list of length `length`, filling missing entries with `default`"""
    return [None for _ in range(length)]


def reduce_until(
    continue_: Callable[[T], bool],
    f: Callable[[T, U], T],
    acc: T,
    collection: Iterable[U],
) -> T:
    """Reduce a value by applying f until continue_ returns False"""
    for item in collection:
        if not continue_(acc):
            break
        acc = f(acc, item)
    return acc


class Marker(Generic[T, U]):
    """Markers are way to annotate (add extra information to) elements of a
    {!val:t}."""

    # @staticmethod
    # def make(length: int, default: Optional[T] = None) -> "Marker[T]":
    #     """Create an Marker of given length, filled with default values"""
    #     return Marker(*[default for _ in range(length)])

    # let make (k : 'k -> int) c (i : 'v) : ('k, 'v) t =
    # let a = Array.make (length c) i in
    # {
    #   get = (fun x -> Array.get a (k x));
    #   set = (fun x v -> Array.set a (k x) v);
    # }
    def __init__(self, key: Callable[[T], int], length: int, default: U) -> None:
        self._data = [default for _ in range(length)]
        self._length = len(self._data)
        self._key = key

    def dummy(self) -> "Marker[T, U]":
        """[dummy k v] create a dummy collection with no element. [k] and [v] are
        only used for typing. Useful for placeholders or for typing purpose."""
        return Marker(lambda x: 0, 0, None)  # type: ignore

    def __getitem__(self, index):
        """[get marker key] Return the annotation associated to [key]."""
        if index < 0 or index >= len(self._data):
            return None
        return self._data[self._key(index)]

    def __setitem__(self, index, value):
        """[set marker key value] Set [value] as annotation associated to [key]."""
        if 0 <= index < len(self._data):
            self._data[self._key(index)] = value

    def __len__(self):
        return self._length

    def __repr__(self):
        return f"Marker({self._data})"

    def __iter__(self):
        return iter(self._data)

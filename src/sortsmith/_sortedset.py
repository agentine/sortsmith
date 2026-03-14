"""SortedSet — a set backed by both a set and a SortedList."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any, Callable, Generic, TypeVar, overload

from sortsmith._sortedlist import SortedKeyList, SortedList, _SupportsLT

T = TypeVar("T", bound=_SupportsLT)


class SortedSet(Generic[T]):
    """A set that maintains its elements in sorted order.

    Backed by a ``set`` for O(1) membership and a ``SortedList`` for ordering.
    """

    __slots__ = ("_set", "_list", "_key")

    def __init__(
        self,
        iterable: Iterable[T] | None = None,
        *,
        key: Callable[[T], Any] | None = None,
    ) -> None:
        self._key = key
        self._set: set[T] = set()
        self._list: SortedList[T] | SortedKeyList[T] = (
            SortedKeyList(key=key) if key is not None else SortedList()
        )
        if iterable is not None:
            self.update(iterable)

    # ---- Mutation ----

    def add(self, value: T) -> None:
        if value not in self._set:
            self._set.add(value)
            self._list.add(value)

    def discard(self, value: T) -> None:
        if value in self._set:
            self._set.discard(value)
            self._list.discard(value)

    def remove(self, value: T) -> None:
        if value not in self._set:
            raise KeyError(value)
        self._set.remove(value)
        self._list.discard(value)

    def pop(self, index: int = -1) -> T:
        val = self._list.pop(index)
        self._set.discard(val)
        return val

    def clear(self) -> None:
        self._set.clear()
        self._list.clear()

    def update(self, iterable: Iterable[T]) -> None:
        for v in iterable:
            self.add(v)

    # ---- Lookup ----

    def __contains__(self, value: object) -> bool:
        return value in self._set

    def __len__(self) -> int:
        return len(self._set)

    def __bool__(self) -> bool:
        return len(self._set) > 0

    def __iter__(self) -> Iterator[T]:
        return iter(self._list)

    def __reversed__(self) -> Iterator[T]:
        return reversed(self._list)

    @overload
    def __getitem__(self, index: int) -> T: ...
    @overload
    def __getitem__(self, index: slice) -> list[T]: ...
    def __getitem__(self, index: int | slice) -> T | list[T]:
        return self._list[index]

    def bisect_left(self, value: T) -> int:
        return self._list.bisect_left(value)

    def bisect_right(self, value: T) -> int:
        return self._list.bisect_right(value)

    bisect = bisect_right

    def count(self, value: T) -> int:
        return 1 if value in self._set else 0

    def index(self, value: T) -> int:
        return self._list.index(value)

    # ---- Range iteration ----

    def irange(
        self,
        minimum: T | None = None,
        maximum: T | None = None,
        inclusive: tuple[bool, bool] = (True, True),
        reverse: bool = False,
    ) -> Iterator[T]:
        return self._list.irange(minimum, maximum, inclusive, reverse)

    def islice(
        self,
        start: int | None = None,
        stop: int | None = None,
        reverse: bool = False,
    ) -> Iterator[T]:
        return self._list.islice(start, stop, reverse)

    # ---- Set operations ----

    def __or__(self, other: SortedSet[T] | set[T]) -> SortedSet[T]:
        result: SortedSet[T] = SortedSet(self._set | (other._set if isinstance(other, SortedSet) else other), key=self._key)
        return result

    def __ior__(self, other: Iterable[T]) -> SortedSet[T]:
        self.update(other)
        return self

    def __and__(self, other: SortedSet[T] | set[T]) -> SortedSet[T]:
        other_set = other._set if isinstance(other, SortedSet) else other
        return SortedSet(self._set & other_set, key=self._key)

    def __iand__(self, other: Iterable[T]) -> SortedSet[T]:
        other_set = set(other)
        to_remove = self._set - other_set
        for v in to_remove:
            self.discard(v)
        return self

    def __sub__(self, other: SortedSet[T] | set[T]) -> SortedSet[T]:
        other_set = other._set if isinstance(other, SortedSet) else other
        return SortedSet(self._set - other_set, key=self._key)

    def __isub__(self, other: Iterable[T]) -> SortedSet[T]:
        for v in other:
            self.discard(v)
        return self

    def __xor__(self, other: SortedSet[T] | set[T]) -> SortedSet[T]:
        other_set = other._set if isinstance(other, SortedSet) else other
        return SortedSet(self._set ^ other_set, key=self._key)

    def __ixor__(self, other: Iterable[T]) -> SortedSet[T]:
        other_set = set(other)
        result = self._set ^ other_set
        self.clear()
        self.update(result)
        return self

    def isdisjoint(self, other: Iterable[T]) -> bool:
        return self._set.isdisjoint(other)

    def issubset(self, other: Iterable[T]) -> bool:
        return self._set.issubset(other)

    def issuperset(self, other: Iterable[T]) -> bool:
        return self._set.issuperset(other)

    # ---- Comparison ----

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SortedSet):
            return self._set == other._set
        if isinstance(other, set):
            return self._set == other
        return NotImplemented

    def __lt__(self, other: SortedSet[T] | set[T]) -> bool:
        other_set = other._set if isinstance(other, SortedSet) else other
        return self._set < other_set

    def __le__(self, other: SortedSet[T] | set[T]) -> bool:
        other_set = other._set if isinstance(other, SortedSet) else other
        return self._set <= other_set

    def __gt__(self, other: SortedSet[T] | set[T]) -> bool:
        other_set = other._set if isinstance(other, SortedSet) else other
        return self._set > other_set

    def __ge__(self, other: SortedSet[T] | set[T]) -> bool:
        other_set = other._set if isinstance(other, SortedSet) else other
        return self._set >= other_set

    # ---- Representation ----

    def __repr__(self) -> str:
        return f"SortedSet({list(self._list)!r})"

    def copy(self) -> SortedSet[T]:
        return SortedSet(self._set, key=self._key)

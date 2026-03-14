"""SortedList — a sorted-order list backed by a segmented list-of-lists."""

from __future__ import annotations

import bisect
from collections.abc import Iterable, Iterator
from itertools import chain
from typing import Any, Callable, Generic, Protocol, TypeVar, overload


class _SupportsLT(Protocol):
    def __lt__(self, __other: Any) -> bool: ...


T = TypeVar("T", bound=_SupportsLT)

_DEFAULT_LOAD = 1000


class SortedList(Generic[T]):
    """A list that maintains its elements in sorted order.

    Uses a segmented list (list-of-lists) with bounded sublist size
    for O(log n) insertion/deletion and O(1) amortized indexed access.
    """

    __slots__ = ("_lists", "_maxes", "_len", "_load", "_index")

    def __init__(
        self,
        iterable: Iterable[T] | None = None,
        *,
        _load: int = _DEFAULT_LOAD,
    ) -> None:
        self._load = _load
        self._lists: list[list[T]] = []
        self._maxes: list[T] = []
        self._len = 0
        self._index: list[int] = []
        if iterable is not None:
            self.update(iterable)

    # ---- Internal helpers ----

    def _build_index(self) -> None:
        """Rebuild the positional index (prefix-sum of sublist lengths)."""
        self._index = [len(sub) for sub in self._lists]

    def _pos(self, idx: int) -> tuple[int, int]:
        """Convert a flat index to (list_index, sublist_index)."""
        if idx < 0 or idx >= self._len:
            raise IndexError("list index out of range")
        if not self._index:
            self._build_index()
        pos = 0
        for i, size in enumerate(self._index):
            if idx < pos + size:
                return i, idx - pos
            pos += size
        raise IndexError("list index out of range")  # pragma: no cover

    def _expand(self, list_idx: int) -> None:
        """Split a sublist that has grown past 2*load."""
        sub = self._lists[list_idx]
        load = self._load
        if len(sub) <= load * 2:
            return
        mid = len(sub) // 2
        right = sub[mid:]
        del sub[mid:]
        self._lists.insert(list_idx + 1, right)
        self._maxes[list_idx] = sub[-1]
        self._maxes.insert(list_idx + 1, right[-1])
        self._index.clear()

    def _delete(self, list_idx: int, sub_idx: int) -> T:
        """Delete element at (list_idx, sub_idx). Returns removed value."""
        sub = self._lists[list_idx]
        val = sub[sub_idx]
        del sub[sub_idx]
        self._len -= 1
        self._index.clear()
        if sub:
            self._maxes[list_idx] = sub[-1]
        else:
            del self._lists[list_idx]
            del self._maxes[list_idx]
        return val

    # ---- Mutation ----

    def add(self, value: T) -> None:
        """Add *value* to the sorted list."""
        if not self._maxes:
            self._lists.append([value])
            self._maxes.append(value)
            self._len += 1
            self._index.clear()
            return
        # Find which sublist to insert into.
        pos = bisect.bisect_right(self._maxes, value)
        if pos == len(self._maxes):
            pos -= 1
        sub = self._lists[pos]
        idx = bisect.bisect_right(sub, value)
        sub.insert(idx, value)
        self._maxes[pos] = sub[-1]
        self._len += 1
        self._index.clear()
        self._expand(pos)

    def discard(self, value: T) -> None:
        """Remove *value* if present; do nothing if absent."""
        if not self._maxes:
            return
        pos = bisect.bisect_left(self._maxes, value)
        if pos == len(self._maxes):
            return
        sub = self._lists[pos]
        idx = bisect.bisect_left(sub, value)
        if idx < len(sub) and sub[idx] == value:
            self._delete(pos, idx)

    def remove(self, value: T) -> None:
        """Remove *value*; raise ValueError if not present."""
        if not self._maxes:
            raise ValueError(f"{value!r} not in list")
        pos = bisect.bisect_left(self._maxes, value)
        if pos == len(self._maxes):
            raise ValueError(f"{value!r} not in list")
        sub = self._lists[pos]
        idx = bisect.bisect_left(sub, value)
        if idx < len(sub) and sub[idx] == value:
            self._delete(pos, idx)
        else:
            raise ValueError(f"{value!r} not in list")

    def pop(self, index: int = -1) -> T:
        """Remove and return item at *index* (default last)."""
        if not self._len:
            raise IndexError("pop from empty list")
        if index < 0:
            index += self._len
        li, si = self._pos(index)
        return self._delete(li, si)

    def clear(self) -> None:
        """Remove all elements."""
        self._lists.clear()
        self._maxes.clear()
        self._len = 0
        self._index.clear()

    def update(self, iterable: Iterable[T]) -> None:
        """Add all values from *iterable*."""
        values = sorted(iterable)
        if not values:
            return
        if not self._maxes:
            # Build sublists from scratch.
            load = self._load
            self._lists = [
                values[i : i + load] for i in range(0, len(values), load)
            ]
            self._maxes = [sub[-1] for sub in self._lists]
            self._len = len(values)
            self._index.clear()
        else:
            for v in values:
                self.add(v)

    # ---- Lookup ----

    def __contains__(self, value: object) -> bool:
        if not self._maxes:
            return False
        try:
            val: Any = value
            pos: int = bisect.bisect_left(self._maxes, val)
        except TypeError:
            return False
        if pos == len(self._maxes):
            return False
        sub = self._lists[pos]
        idx = bisect.bisect_left(sub, val)
        return idx < len(sub) and sub[idx] == value

    def __len__(self) -> int:
        return self._len

    def __bool__(self) -> bool:
        return self._len > 0

    def __iter__(self) -> Iterator[T]:
        return chain.from_iterable(self._lists)

    def __reversed__(self) -> Iterator[T]:
        for sub in reversed(self._lists):
            yield from reversed(sub)

    @overload
    def __getitem__(self, index: int) -> T: ...
    @overload
    def __getitem__(self, index: slice) -> list[T]: ...
    def __getitem__(self, index: int | slice) -> T | list[T]:
        if isinstance(index, slice):
            start, stop, step = index.indices(self._len)
            return [self[i] for i in range(start, stop, step)]
        if index < 0:
            index += self._len
        li, si = self._pos(index)
        return self._lists[li][si]

    @overload
    def __delitem__(self, index: int) -> None: ...
    @overload
    def __delitem__(self, index: slice) -> None: ...
    def __delitem__(self, index: int | slice) -> None:
        if isinstance(index, slice):
            indices = range(*index.indices(self._len))
            # Delete in reverse order to keep indices stable.
            for i in sorted(indices, reverse=True):
                self.pop(i)
            return
        if index < 0:
            index += self._len
        li, si = self._pos(index)
        self._delete(li, si)

    def bisect_left(self, value: T) -> int:
        """Return the index where *value* would be inserted (left)."""
        if not self._maxes:
            return 0
        pos = bisect.bisect_left(self._maxes, value)
        if pos == len(self._maxes):
            return self._len
        sub = self._lists[pos]
        idx = bisect.bisect_left(sub, value)
        # Count elements before this sublist.
        return sum(len(self._lists[i]) for i in range(pos)) + idx

    def bisect_right(self, value: T) -> int:
        """Return the index where *value* would be inserted (right)."""
        if not self._maxes:
            return 0
        pos = bisect.bisect_right(self._maxes, value)
        if pos == len(self._maxes):
            return self._len
        sub = self._lists[pos]
        idx = bisect.bisect_right(sub, value)
        return sum(len(self._lists[i]) for i in range(pos)) + idx

    bisect = bisect_right

    def index(
        self,
        value: T,
        start: int | None = None,
        stop: int | None = None,
    ) -> int:
        """Return the smallest index *i* where ``self[i] == value``.

        Raises ValueError if *value* is not found within [start, stop).
        """
        if start is None:
            start = 0
        if stop is None:
            stop = self._len
        if start < 0:
            start += self._len
        if stop < 0:
            stop += self._len
        start = max(start, 0)
        stop = min(stop, self._len)

        bl = self.bisect_left(value)
        if bl < stop and bl >= start and bl < self._len and self[bl] == value:
            return bl
        raise ValueError(f"{value!r} is not in list")

    def count(self, value: T) -> int:
        """Return the number of occurrences of *value*."""
        left = self.bisect_left(value)
        right = self.bisect_right(value)
        return right - left

    # ---- Range iteration ----

    def irange(
        self,
        minimum: T | None = None,
        maximum: T | None = None,
        inclusive: tuple[bool, bool] = (True, True),
        reverse: bool = False,
    ) -> Iterator[T]:
        """Iterate over values in [minimum, maximum] (by default inclusive)."""
        inc_min, inc_max = inclusive

        if minimum is None:
            start = 0
        elif inc_min:
            start = self.bisect_left(minimum)
        else:
            start = self.bisect_right(minimum)

        if maximum is None:
            stop = self._len
        elif inc_max:
            stop = self.bisect_right(maximum)
        else:
            stop = self.bisect_left(maximum)

        if reverse:
            for i in range(stop - 1, start - 1, -1):
                yield self[i]
        else:
            for i in range(start, stop):
                yield self[i]

    def islice(
        self,
        start: int | None = None,
        stop: int | None = None,
        reverse: bool = False,
    ) -> Iterator[T]:
        """Iterate over a positional slice."""
        if start is None:
            start = 0
        if stop is None:
            stop = self._len
        if start < 0:
            start += self._len
        if stop < 0:
            stop += self._len
        start = max(start, 0)
        stop = min(stop, self._len)
        if reverse:
            for i in range(stop - 1, start - 1, -1):
                yield self[i]
        else:
            for i in range(start, stop):
                yield self[i]

    # ---- Operators ----

    def __add__(self, other: SortedList[T]) -> SortedList[T]:
        result: SortedList[T] = SortedList(self, _load=self._load)
        result.update(other)
        return result

    def __iadd__(self, other: Iterable[T]) -> SortedList[T]:
        self.update(other)
        return self

    def __mul__(self, num: int) -> SortedList[T]:
        result: SortedList[T] = SortedList(_load=self._load)
        for _ in range(num):
            result.update(self)
        return result

    def __imul__(self, num: int) -> SortedList[T]:
        if num <= 0:
            self.clear()
            return self
        if num == 1:
            return self
        values = list(self)
        for _ in range(num - 1):
            self.update(values)
        return self

    # ---- Comparison ----

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SortedList):
            return list(self) == list(other)
        return NotImplemented

    def __lt__(self, other: SortedList[T]) -> bool:
        return list(self) < list(other)

    def __le__(self, other: SortedList[T]) -> bool:
        return list(self) <= list(other)

    def __gt__(self, other: SortedList[T]) -> bool:
        return list(self) > list(other)

    def __ge__(self, other: SortedList[T]) -> bool:
        return list(self) >= list(other)

    # ---- Representation ----

    def __repr__(self) -> str:
        return f"SortedList({list(self)!r})"

    def copy(self) -> SortedList[T]:
        """Return a shallow copy."""
        return SortedList(self, _load=self._load)


K = TypeVar("K", bound=_SupportsLT)


class SortedKeyList(Generic[T]):
    """A sorted list that uses a key function for ordering.

    Elements are ordered by ``key(element)`` but stored as-is.
    """

    __slots__ = ("_key", "_keys", "_list")

    def __init__(
        self,
        iterable: Iterable[T] | None = None,
        *,
        key: Callable[[T], Any] | None = None,
    ) -> None:
        if key is None:
            raise TypeError("SortedKeyList requires a key function")
        self._key: Callable[[T], Any] = key
        self._keys: list[Any] = []
        self._list: list[T] = []
        if iterable is not None:
            self.update(iterable)

    @property
    def key(self) -> Callable[[T], Any]:
        return self._key

    # ---- Internal ----

    def _rebuild_keys(self) -> None:
        self._keys = [self._key(v) for v in self._list]

    # ---- Mutation ----

    def add(self, value: T) -> None:
        k = self._key(value)
        idx = bisect.bisect_right(self._keys, k)
        self._keys.insert(idx, k)
        self._list.insert(idx, value)

    def discard(self, value: T) -> None:
        k = self._key(value)
        idx = bisect.bisect_left(self._keys, k)
        while idx < len(self._keys) and self._keys[idx] == k:
            if self._list[idx] == value:
                del self._keys[idx]
                del self._list[idx]
                return
            idx += 1

    def remove(self, value: T) -> None:
        k = self._key(value)
        idx = bisect.bisect_left(self._keys, k)
        while idx < len(self._keys) and self._keys[idx] == k:
            if self._list[idx] == value:
                del self._keys[idx]
                del self._list[idx]
                return
            idx += 1
        raise ValueError(f"{value!r} not in list")

    def pop(self, index: int = -1) -> T:
        val = self._list.pop(index)
        if index < 0:
            index += len(self._keys) + 1
        del self._keys[index]
        return val

    def clear(self) -> None:
        self._keys.clear()
        self._list.clear()

    def update(self, iterable: Iterable[T]) -> None:
        for v in iterable:
            self.add(v)

    # ---- Lookup ----

    def __contains__(self, value: object) -> bool:
        try:
            k = self._key(value)  # type: ignore[arg-type]
        except TypeError:
            return False
        idx = bisect.bisect_left(self._keys, k)
        while idx < len(self._keys) and self._keys[idx] == k:
            if self._list[idx] == value:
                return True
            idx += 1
        return False

    def __len__(self) -> int:
        return len(self._list)

    def __bool__(self) -> bool:
        return len(self._list) > 0

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

    @overload
    def __delitem__(self, index: int) -> None: ...
    @overload
    def __delitem__(self, index: slice) -> None: ...
    def __delitem__(self, index: int | slice) -> None:
        del self._list[index]
        if isinstance(index, slice):
            self._rebuild_keys()
        else:
            if index < 0:
                index += len(self._keys)
            del self._keys[index]

    def bisect_left(self, value: T) -> int:
        k = self._key(value)
        return bisect.bisect_left(self._keys, k)

    def bisect_right(self, value: T) -> int:
        k = self._key(value)
        return bisect.bisect_right(self._keys, k)

    bisect = bisect_right

    def bisect_key_left(self, key: Any) -> int:
        return bisect.bisect_left(self._keys, key)

    def bisect_key_right(self, key: Any) -> int:
        return bisect.bisect_right(self._keys, key)

    def index(
        self,
        value: T,
        start: int | None = None,
        stop: int | None = None,
    ) -> int:
        if start is None:
            start = 0
        if stop is None:
            stop = len(self._list)
        k = self._key(value)
        idx = bisect.bisect_left(self._keys, k)
        while idx < stop and self._keys[idx] == k:
            if idx >= start and self._list[idx] == value:
                return idx
            idx += 1
        raise ValueError(f"{value!r} is not in list")

    def count(self, value: T) -> int:
        k = self._key(value)
        left = bisect.bisect_left(self._keys, k)
        right = bisect.bisect_right(self._keys, k)
        return sum(1 for i in range(left, right) if self._list[i] == value)

    # ---- Range iteration ----

    def irange(
        self,
        minimum: T | None = None,
        maximum: T | None = None,
        inclusive: tuple[bool, bool] = (True, True),
        reverse: bool = False,
    ) -> Iterator[T]:
        inc_min, inc_max = inclusive
        if minimum is None:
            start = 0
        else:
            mk = self._key(minimum)
            start = bisect.bisect_left(self._keys, mk) if inc_min else bisect.bisect_right(self._keys, mk)
        if maximum is None:
            stop = len(self._list)
        else:
            mk = self._key(maximum)
            stop = bisect.bisect_right(self._keys, mk) if inc_max else bisect.bisect_left(self._keys, mk)
        rng = range(stop - 1, start - 1, -1) if reverse else range(start, stop)
        for i in rng:
            yield self._list[i]

    def irange_key(
        self,
        min_key: Any = None,
        max_key: Any = None,
        inclusive: tuple[bool, bool] = (True, True),
        reverse: bool = False,
    ) -> Iterator[T]:
        """Iterate over values whose keys are in [min_key, max_key]."""
        inc_min, inc_max = inclusive
        if min_key is None:
            start = 0
        elif inc_min:
            start = bisect.bisect_left(self._keys, min_key)
        else:
            start = bisect.bisect_right(self._keys, min_key)
        if max_key is None:
            stop = len(self._list)
        elif inc_max:
            stop = bisect.bisect_right(self._keys, max_key)
        else:
            stop = bisect.bisect_left(self._keys, max_key)
        rng = range(stop - 1, start - 1, -1) if reverse else range(start, stop)
        for i in rng:
            yield self._list[i]

    def islice(
        self,
        start: int | None = None,
        stop: int | None = None,
        reverse: bool = False,
    ) -> Iterator[T]:
        n = len(self._list)
        s = 0 if start is None else (start + n if start < 0 else start)
        e = n if stop is None else (stop + n if stop < 0 else stop)
        s = max(s, 0)
        e = min(e, n)
        rng = range(e - 1, s - 1, -1) if reverse else range(s, e)
        for i in rng:
            yield self._list[i]

    # ---- Representation ----

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SortedKeyList):
            return self._list == other._list
        return NotImplemented

    def __repr__(self) -> str:
        return f"SortedKeyList({self._list!r}, key={self._key!r})"

    def copy(self) -> SortedKeyList[T]:
        return SortedKeyList(self._list, key=self._key)

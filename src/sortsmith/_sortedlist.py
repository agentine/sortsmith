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
        """Rebuild the positional index (cumulative prefix sums)."""
        cum = 0
        self._index = []
        for sub in self._lists:
            cum += len(sub)
            self._index.append(cum)

    def _pos(self, idx: int) -> tuple[int, int]:
        """Convert a flat index to (list_index, sublist_index)."""
        if idx < 0 or idx >= self._len:
            raise IndexError("list index out of range")
        if not self._index:
            self._build_index()
        # Binary search on cumulative sums.
        i = bisect.bisect_right(self._index, idx)
        if i >= len(self._index):
            raise IndexError("list index out of range")  # pragma: no cover
        offset = 0 if i == 0 else self._index[i - 1]
        return i, idx - offset

    def _offset(self, list_idx: int) -> int:
        """Return the flat offset of the start of sublist at list_idx."""
        if not self._index:
            self._build_index()
        return 0 if list_idx == 0 else self._index[list_idx - 1]

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
        return self._offset(pos) + idx

    def bisect_right(self, value: T) -> int:
        """Return the index where *value* would be inserted (right)."""
        if not self._maxes:
            return 0
        pos = bisect.bisect_right(self._maxes, value)
        if pos == len(self._maxes):
            return self._len
        sub = self._lists[pos]
        idx = bisect.bisect_right(sub, value)
        return self._offset(pos) + idx

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
    Uses a segmented list-of-lists for O(log n) insert/delete.
    """

    __slots__ = (
        "_key", "_lists", "_key_lists", "_maxes", "_len", "_load", "_index",
    )

    def __init__(
        self,
        iterable: Iterable[T] | None = None,
        *,
        key: Callable[[T], Any] | None = None,
        _load: int = _DEFAULT_LOAD,
    ) -> None:
        if key is None:
            raise TypeError("SortedKeyList requires a key function")
        self._key: Callable[[T], Any] = key
        self._load = _load
        self._lists: list[list[T]] = []
        self._key_lists: list[list[Any]] = []
        self._maxes: list[Any] = []
        self._len = 0
        self._index: list[int] = []
        if iterable is not None:
            self.update(iterable)

    @property
    def key(self) -> Callable[[T], Any]:
        return self._key

    # ---- Internal ----

    def _build_index(self) -> None:
        cum = 0
        self._index = []
        for sub in self._lists:
            cum += len(sub)
            self._index.append(cum)

    def _pos(self, idx: int) -> tuple[int, int]:
        if idx < 0 or idx >= self._len:
            raise IndexError("list index out of range")
        if not self._index:
            self._build_index()
        i = bisect.bisect_right(self._index, idx)
        if i >= len(self._index):
            raise IndexError("list index out of range")  # pragma: no cover
        offset = 0 if i == 0 else self._index[i - 1]
        return i, idx - offset

    def _offset(self, list_idx: int) -> int:
        if not self._index:
            self._build_index()
        return 0 if list_idx == 0 else self._index[list_idx - 1]

    def _expand(self, list_idx: int) -> None:
        sub = self._lists[list_idx]
        if len(sub) <= self._load * 2:
            return
        keys = self._key_lists[list_idx]
        mid = len(sub) // 2
        self._lists.insert(list_idx + 1, sub[mid:])
        self._key_lists.insert(list_idx + 1, keys[mid:])
        del sub[mid:]
        del keys[mid:]
        self._maxes[list_idx] = keys[-1]
        self._maxes.insert(list_idx + 1, self._key_lists[list_idx + 1][-1])
        self._index.clear()

    def _delete(self, list_idx: int, sub_idx: int) -> T:
        sub = self._lists[list_idx]
        keys = self._key_lists[list_idx]
        val = sub[sub_idx]
        del sub[sub_idx]
        del keys[sub_idx]
        self._len -= 1
        self._index.clear()
        if sub:
            self._maxes[list_idx] = keys[-1]
        else:
            del self._lists[list_idx]
            del self._key_lists[list_idx]
            del self._maxes[list_idx]
        return val

    # ---- Mutation ----

    def add(self, value: T) -> None:
        k = self._key(value)
        if not self._maxes:
            self._lists.append([value])
            self._key_lists.append([k])
            self._maxes.append(k)
            self._len += 1
            self._index.clear()
            return
        pos = bisect.bisect_right(self._maxes, k)
        if pos == len(self._maxes):
            pos -= 1
        keys = self._key_lists[pos]
        idx = bisect.bisect_right(keys, k)
        self._lists[pos].insert(idx, value)
        keys.insert(idx, k)
        self._maxes[pos] = keys[-1]
        self._len += 1
        self._index.clear()
        self._expand(pos)

    def discard(self, value: T) -> None:
        k = self._key(value)
        if not self._maxes:
            return
        pos = bisect.bisect_left(self._maxes, k)
        if pos == len(self._maxes):
            return
        while pos < len(self._maxes):
            keys = self._key_lists[pos]
            idx = bisect.bisect_left(keys, k)
            while idx < len(keys) and keys[idx] == k:
                if self._lists[pos][idx] == value:
                    self._delete(pos, idx)
                    return
                idx += 1
            pos += 1
            if pos < len(self._maxes) and self._maxes[pos - 1] != k:
                break

    def remove(self, value: T) -> None:
        k = self._key(value)
        if not self._maxes:
            raise ValueError(f"{value!r} not in list")
        pos = bisect.bisect_left(self._maxes, k)
        if pos == len(self._maxes):
            raise ValueError(f"{value!r} not in list")
        while pos < len(self._maxes):
            keys = self._key_lists[pos]
            idx = bisect.bisect_left(keys, k)
            while idx < len(keys) and keys[idx] == k:
                if self._lists[pos][idx] == value:
                    self._delete(pos, idx)
                    return
                idx += 1
            pos += 1
            if pos < len(self._maxes) and self._maxes[pos - 1] != k:
                break
        raise ValueError(f"{value!r} not in list")

    def pop(self, index: int = -1) -> T:
        if not self._len:
            raise IndexError("pop from empty list")
        if index < 0:
            index += self._len
        li, si = self._pos(index)
        return self._delete(li, si)

    def clear(self) -> None:
        self._lists.clear()
        self._key_lists.clear()
        self._maxes.clear()
        self._len = 0
        self._index.clear()

    def update(self, iterable: Iterable[T]) -> None:
        values = list(iterable)
        if not values:
            return
        values.sort(key=self._key)
        if not self._maxes:
            load = self._load
            self._lists = [
                values[i : i + load] for i in range(0, len(values), load)
            ]
            self._key_lists = [
                [self._key(v) for v in sub] for sub in self._lists
            ]
            self._maxes = [keys[-1] for keys in self._key_lists]
            self._len = len(values)
            self._index.clear()
        else:
            for v in values:
                self.add(v)

    # ---- Lookup ----

    def __contains__(self, value: object) -> bool:
        try:
            k = self._key(value)  # type: ignore[arg-type]
        except TypeError:
            return False
        if not self._maxes:
            return False
        pos = bisect.bisect_left(self._maxes, k)
        if pos == len(self._maxes):
            return False
        while pos < len(self._maxes):
            keys = self._key_lists[pos]
            idx = bisect.bisect_left(keys, k)
            while idx < len(keys) and keys[idx] == k:
                if self._lists[pos][idx] == value:
                    return True
                idx += 1
            pos += 1
            if pos < len(self._maxes) and self._maxes[pos - 1] != k:
                break
        return False

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
            for i in sorted(indices, reverse=True):
                self.pop(i)
            return
        if index < 0:
            index += self._len
        li, si = self._pos(index)
        self._delete(li, si)

    def bisect_left(self, value: T) -> int:
        k = self._key(value)
        return self.bisect_key_left(k)

    def bisect_right(self, value: T) -> int:
        k = self._key(value)
        return self.bisect_key_right(k)

    bisect = bisect_right

    def bisect_key_left(self, key: Any) -> int:
        if not self._maxes:
            return 0
        pos = bisect.bisect_left(self._maxes, key)
        if pos == len(self._maxes):
            return self._len
        keys = self._key_lists[pos]
        idx = bisect.bisect_left(keys, key)
        return self._offset(pos) + idx

    def bisect_key_right(self, key: Any) -> int:
        if not self._maxes:
            return 0
        pos = bisect.bisect_right(self._maxes, key)
        if pos == len(self._maxes):
            return self._len
        keys = self._key_lists[pos]
        idx = bisect.bisect_right(keys, key)
        return self._offset(pos) + idx

    def index(
        self,
        value: T,
        start: int | None = None,
        stop: int | None = None,
    ) -> int:
        if start is None:
            start = 0
        if stop is None:
            stop = self._len
        bl = self.bisect_left(value)
        if bl < stop and bl >= start and bl < self._len and self[bl] == value:
            return bl
        raise ValueError(f"{value!r} is not in list")

    def count(self, value: T) -> int:
        left = self.bisect_left(value)
        right = self.bisect_right(value)
        return sum(1 for i in range(left, right) if self[i] == value)

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
            start = self.bisect_key_left(mk) if inc_min else self.bisect_key_right(mk)
        if maximum is None:
            stop = self._len
        else:
            mk = self._key(maximum)
            stop = self.bisect_key_right(mk) if inc_max else self.bisect_key_left(mk)
        rng = range(stop - 1, start - 1, -1) if reverse else range(start, stop)
        for i in rng:
            yield self[i]

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
            start = self.bisect_key_left(min_key)
        else:
            start = self.bisect_key_right(min_key)
        if max_key is None:
            stop = self._len
        elif inc_max:
            stop = self.bisect_key_right(max_key)
        else:
            stop = self.bisect_key_left(max_key)
        rng = range(stop - 1, start - 1, -1) if reverse else range(start, stop)
        for i in rng:
            yield self[i]

    def islice(
        self,
        start: int | None = None,
        stop: int | None = None,
        reverse: bool = False,
    ) -> Iterator[T]:
        s = 0 if start is None else (start + self._len if start < 0 else start)
        e = self._len if stop is None else (stop + self._len if stop < 0 else stop)
        s = max(s, 0)
        e = min(e, self._len)
        rng = range(e - 1, s - 1, -1) if reverse else range(s, e)
        for i in rng:
            yield self[i]

    # ---- Representation ----

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SortedKeyList):
            return list(self) == list(other)
        return NotImplemented

    def __repr__(self) -> str:
        return f"SortedKeyList({list(self)!r}, key={self._key!r})"

    def copy(self) -> SortedKeyList[T]:
        return SortedKeyList(self, key=self._key, _load=self._load)

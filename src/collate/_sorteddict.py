"""SortedDict — a dict subclass with keys maintained in sorted order."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Callable, Generic, TypeVar, overload

from collate._sortedlist import SortedKeyList, SortedList, _SupportsLT

K = TypeVar("K", bound=_SupportsLT)
V = TypeVar("V")


class _IlocProxy(Generic[K, V]):
    """Positional indexing proxy for SortedDict keys."""

    __slots__ = ("_sd",)

    def __init__(self, sd: SortedDict[K, V]) -> None:
        self._sd = sd

    @overload
    def __getitem__(self, index: int) -> K: ...
    @overload
    def __getitem__(self, index: slice) -> list[K]: ...
    def __getitem__(self, index: int | slice) -> K | list[K]:
        return self._sd._keys[index]

    def __len__(self) -> int:
        return len(self._sd._keys)


class SortedDict(dict[K, V]):
    """A dict subclass whose keys are kept in sorted order."""

    _keys: SortedList[K] | SortedKeyList[K]
    _key_func: Callable[[K], Any] | None

    def __init__(
        self,
        __key_or_mapping: Callable[[K], Any] | dict[K, V] | None = None,
        /,
        *args: Any,
        **kwargs: V,
    ) -> None:
        key_func: Callable[[K], Any] | None = None
        mapping_args: tuple[Any, ...] = args
        mapping_kw: dict[str, V] = kwargs

        if callable(__key_or_mapping) and not isinstance(__key_or_mapping, dict):
            key_func = __key_or_mapping
            # args/kwargs are the mapping data
        elif __key_or_mapping is not None:
            mapping_args = (__key_or_mapping, *args)

        self._key_func = key_func
        super().__init__(*mapping_args, **mapping_kw)
        # Build _keys from whatever dict.__init__ put in.
        if key_func is not None:
            self._keys = SortedKeyList(super().keys(), key=key_func)
        else:
            self._keys = SortedList(super().keys())

    @property
    def key(self) -> Callable[[K], Any] | None:
        return self._key_func

    # ---- dict overrides ----

    def __setitem__(self, key: K, value: V) -> None:
        if key not in self:
            self._keys.add(key)
        super().__setitem__(key, value)

    def __delitem__(self, key: K) -> None:
        super().__delitem__(key)
        self._keys.discard(key)

    def clear(self) -> None:
        super().clear()
        self._keys.clear()

    def pop(self, key: K, *args: Any) -> Any:
        if key in self:
            self._keys.discard(key)
        return super().pop(key, *args)

    def update(self, __m: Any = (), /, **kwargs: Any) -> None:
        if hasattr(__m, "keys"):
            for k in __m.keys():
                self[k] = __m[k]
        else:
            for k, v in __m:
                self[k] = v
        for k_str, v in kwargs.items():
            self[k_str] = v  # type: ignore[index]

    def setdefault(self, key: K, default: Any = None) -> Any:
        if key not in self:
            self[key] = default
        return self[key]

    # ---- Sorted views ----

    def keys(self) -> SortedKeysView[K, V]:  # type: ignore[override]
        return SortedKeysView(self)

    def values(self) -> SortedValuesView[K, V]:  # type: ignore[override]
        return SortedValuesView(self)

    def items(self) -> SortedItemsView[K, V]:  # type: ignore[override]
        return SortedItemsView(self)

    # ---- Positional access ----

    @property
    def iloc(self) -> _IlocProxy[K, V]:
        return _IlocProxy(self)

    def peekitem(self, index: int = -1) -> tuple[K, V]:
        """Return (key, value) at sorted index without removing."""
        key = self._keys[index]
        return key, self[key]

    def popitem(self, index: int = -1) -> tuple[K, V]:
        """Remove and return (key, value) at sorted index."""
        key = self._keys[index]
        value = super().pop(key)
        self._keys.discard(key)
        return key, value

    # ---- Sorted operations ----

    def irange(
        self,
        minimum: K | None = None,
        maximum: K | None = None,
        inclusive: tuple[bool, bool] = (True, True),
        reverse: bool = False,
    ) -> Iterator[K]:
        return self._keys.irange(minimum, maximum, inclusive, reverse)

    def bisect_left(self, key: K) -> int:
        return self._keys.bisect_left(key)

    def bisect_right(self, key: K) -> int:
        return self._keys.bisect_right(key)

    bisect = bisect_right

    # ---- Representation ----

    def __repr__(self) -> str:
        items = ", ".join(f"{k!r}: {self[k]!r}" for k in self._keys)
        return f"SortedDict({{{items}}})"

    def copy(self) -> SortedDict[K, V]:
        if self._key_func is not None:
            return SortedDict(self._key_func, dict(self))
        return SortedDict(dict(self))

    def __or__(self, other: dict[K, V]) -> SortedDict[K, V]:  # type: ignore[override]
        result = self.copy()
        result.update(other)
        return result

    def __ior__(self, other: dict[K, V]) -> SortedDict[K, V]:  # type: ignore[override]
        self.update(other)
        return self

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)

    def __ne__(self, other: object) -> bool:
        return super().__ne__(other)


class SortedKeysView(Generic[K, V]):
    __slots__ = ("_sd",)

    def __init__(self, sd: SortedDict[K, V]) -> None:
        self._sd = sd

    def __iter__(self) -> Iterator[K]:
        return iter(self._sd._keys)

    def __reversed__(self) -> Iterator[K]:
        return reversed(self._sd._keys)

    def __len__(self) -> int:
        return len(self._sd._keys)

    def __contains__(self, key: object) -> bool:
        return key in self._sd

    def __repr__(self) -> str:
        return f"SortedKeysView({list(self._sd._keys)!r})"


class SortedValuesView(Generic[K, V]):
    __slots__ = ("_sd",)

    def __init__(self, sd: SortedDict[K, V]) -> None:
        self._sd = sd

    def __iter__(self) -> Iterator[V]:
        for k in self._sd._keys:
            yield self._sd[k]

    def __reversed__(self) -> Iterator[V]:
        for k in reversed(self._sd._keys):
            yield self._sd[k]

    def __len__(self) -> int:
        return len(self._sd._keys)

    def __repr__(self) -> str:
        return f"SortedValuesView({list(self)!r})"


class SortedItemsView(Generic[K, V]):
    __slots__ = ("_sd",)

    def __init__(self, sd: SortedDict[K, V]) -> None:
        self._sd = sd

    def __iter__(self) -> Iterator[tuple[K, V]]:
        for k in self._sd._keys:
            yield k, self._sd[k]

    def __reversed__(self) -> Iterator[tuple[K, V]]:
        for k in reversed(self._sd._keys):
            yield k, self._sd[k]

    def __len__(self) -> int:
        return len(self._sd._keys)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, tuple) or len(item) != 2:
            return False
        key, value = item
        return key in self._sd and self._sd[key] == value

    def __repr__(self) -> str:
        return f"SortedItemsView({list(self)!r})"

# sortsmith

[![CI](https://github.com/agentine/sortsmith/actions/workflows/ci.yml/badge.svg)](https://github.com/agentine/sortsmith/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/sortsmith)](https://pypi.org/project/sortsmith/)
[![Python](https://img.shields.io/pypi/pyversions/sortsmith)](https://pypi.org/project/sortsmith/)

Pure-Python sorted containers — `SortedList`, `SortedDict`, `SortedSet`, `SortedKeyList`.

Drop-in replacement for [sortedcontainers](https://github.com/grantjenks/python-sortedcontainers) with full type annotations, Python 3.10+ support, and modern packaging.

## Installation

```bash
pip install sortsmith
```

## Quick Start

```python
from sortsmith import SortedList, SortedDict, SortedSet

sl = SortedList([3, 1, 2])    # SortedList([1, 2, 3])
sd = SortedDict(b=2, a=1)     # SortedDict({'a': 1, 'b': 2})
ss = SortedSet([3, 1, 2])     # SortedSet([1, 2, 3])
```

## API Reference

### SortedList

A list that maintains elements in sorted order using a segmented list-of-lists structure — O(log n) insertion/deletion, O(1) amortized indexed access.

```python
from sortsmith import SortedList

sl = SortedList([5, 1, 3])
# SortedList([1, 3, 5])
```

**Mutation**

| Method | Description |
|--------|-------------|
| `add(value)` | Add a value |
| `discard(value)` | Remove if present, no-op otherwise |
| `remove(value)` | Remove; raise `ValueError` if absent |
| `pop(index=-1)` | Remove and return item at index |
| `update(iterable)` | Add all values from iterable |
| `clear()` | Remove all elements |

**Lookup**

| Method / Operator | Description |
|-------------------|-------------|
| `value in sl` | O(log n) membership test |
| `sl[i]` | Index access (int or slice) |
| `del sl[i]` | Delete by index (int or slice) |
| `len(sl)` | Number of elements |
| `bisect_left(value)` | Leftmost insertion point |
| `bisect_right(value)` | Rightmost insertion point |
| `index(value)` | First index of value (raises `ValueError` if absent) |
| `count(value)` | Count occurrences |

**Range iteration**

```python
# Values between 2 and 8 inclusive
list(sl.irange(2, 8))

# Values from index 1 to 4 (exclusive)
list(sl.islice(1, 4))

# Reverse iteration
list(sl.irange(2, 8, reverse=True))

# Exclusive bounds
list(sl.irange(2, 8, inclusive=(False, True)))
```

**Operators**

```python
sl1 + sl2       # New SortedList with all elements
sl += [4, 6]    # In-place update
sl * 2          # New SortedList with elements repeated twice
```

---

### SortedKeyList

Like `SortedList` but ordered by a key function. Elements are stored as-is; only ordering uses the key.

```python
from sortsmith import SortedKeyList

skl = SortedKeyList(["banana", "apple", "cherry"], key=len)
# Ordered by string length: ['apple', 'banana', 'cherry']

skl = SortedKeyList(["banana", "apple", "cherry"], key=str.lower)
```

**Additional methods** (beyond SortedList):

| Method | Description |
|--------|-------------|
| `bisect_key_left(key)` | Leftmost insertion point by key value |
| `bisect_key_right(key)` | Rightmost insertion point by key value |
| `irange_key(min_key, max_key)` | Iterate over values whose keys are in range |
| `skl.key` | The key function |

---

### SortedDict

A `dict` subclass whose keys are kept in sorted order. All dict operations are supported; keys/values/items views iterate in sorted key order.

```python
from sortsmith import SortedDict

sd = SortedDict({"c": 3, "a": 1, "b": 2})
# SortedDict({'a': 1, 'b': 2, 'c': 3})

list(sd.keys())    # ['a', 'b', 'c']
list(sd.values())  # [1, 2, 3]
list(sd.items())   # [('a', 1), ('b', 2), ('c', 3)]

# Direct iteration and reversed() also follow sorted key order
list(sd)           # ['a', 'b', 'c']
list(reversed(sd)) # ['c', 'b', 'a']
```

**Positional access**

```python
sd.peekitem(0)    # ('a', 1) — first item by key, no removal
sd.peekitem(-1)   # ('c', 3) — last item by key, no removal
sd.popitem(0)     # ('a', 1) — remove and return first item

sd.iloc[0]        # 'a' — key at sorted position 0
sd.iloc[-1]       # 'c' — key at last sorted position
sd.iloc[1:3]      # ['b', 'c'] — slice of sorted keys
```

**Range iteration over keys**

```python
list(sd.irange("a", "b"))             # ['a', 'b']
list(sd.irange("a", "b", inclusive=(True, False)))  # ['a']
list(sd.irange(reverse=True))         # ['c', 'b', 'a']
```

**Bisect**

```python
sd.bisect_left("b")   # 1
sd.bisect_right("b")  # 2
```

**Key function**

```python
# Sort keys case-insensitively
sd = SortedDict(str.lower, {"Banana": 1, "apple": 2, "Cherry": 3})
list(sd.keys())  # ['apple', 'Banana', 'Cherry']
```

---

### SortedSet

A set that maintains elements in sorted order. Backed by a `set` (O(1) membership) and a `SortedList` (for ordering and range queries).

```python
from sortsmith import SortedSet

ss = SortedSet([3, 1, 4, 1, 5])
# SortedSet([1, 3, 4, 5]) — duplicates removed, sorted

3 in ss    # True (O(1))
ss[0]      # 1 — indexed access
```

**Mutation**

| Method | Description |
|--------|-------------|
| `add(value)` | Add value (no-op if already present) |
| `discard(value)` | Remove if present |
| `remove(value)` | Remove; raise `KeyError` if absent |
| `pop(index=-1)` | Remove and return item at sorted index |
| `update(iterable)` | Add all values from iterable |
| `clear()` | Remove all elements |

**Set operations** (return new `SortedSet`)

```python
ss1 | ss2    # Union
ss1 & ss2    # Intersection
ss1 - ss2    # Difference
ss1 ^ ss2    # Symmetric difference

ss1 <= ss2   # Subset
ss1 >= ss2   # Superset
```

**Range iteration and positional access**

```python
list(ss.irange(2, 5))          # Values between 2 and 5
list(ss.islice(1, 3))          # Values at sorted positions 1–2
ss.bisect_left(3)              # Insertion point
```

**Key function**

```python
ss = SortedSet(["banana", "apple", "cherry"], key=len)
list(ss)    # ['apple', 'banana', 'cherry']
```

---

## Performance Notes

All four classes use a **segmented list** (list-of-lists) data structure with a configurable load factor (default: 1 000 elements per sublist). This gives amortised O(log n) for insertions and deletions, and O(1) amortised for indexed access.

| Operation | Complexity |
|-----------|-----------|
| `add(value)` | O(log n) |
| `discard(value)` / `remove(value)` | O(log n) |
| `sl[i]` (index access) | O(log n) |
| `value in sl` | O(log n) |
| `bisect_left` / `bisect_right` | O(log n) |
| `update(iterable)` (bulk, empty list) | O(k log k) |
| `update(iterable)` (incremental) | O(k log n) |
| `irange` / `islice` | O(log n + output) |
| `len(sl)` | O(1) |

**Memory:** The segmented structure stores at most ~2× the elements in sublist arrays. No external allocations — pure CPython lists throughout.

**Bulk construction:** Initialising with a large iterable is significantly faster than repeated `add()` calls. When the list is empty, `update()` sorts the input once (O(k log k)) and builds sublists directly.

## Migration from sortedcontainers

```python
# Before
from sortedcontainers import SortedList, SortedDict, SortedSet

# After
from sortsmith import SortedList, SortedDict, SortedSet
```

The API is identical. A global search-and-replace is all that's needed.

**Improvements over sortedcontainers:**

| Feature | sortedcontainers | sortsmith |
|---------|-----------------|---------|
| Last release | May 2021 | Active |
| Python support | 3.7–3.12 | 3.10+ |
| Type annotations | Minimal | Full generics (`SortedList[T]`, `SortedDict[K, V]`, `SortedSet[T]`) |
| mypy strict | No | Yes |
| Packaging | setup.py | pyproject.toml + src layout |

## License

Apache-2.0

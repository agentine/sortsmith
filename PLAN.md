# SortSmith — Implementation Plan

## Overview

**SortSmith** is a pure-Python sorted containers library providing `SortedList`, `SortedDict`, and `SortedSet`. It replaces [`sortedcontainers`](https://github.com/grantjenks/python-sortedcontainers) (179M downloads/month), which has not been released since May 2021, has not received a commit since October 2022, and is maintained by a single developer.

**Package name:** `sortsmith` (verified available on PyPI)
**Language:** Python
**License:** Apache-2.0

## Target Library Assessment

| Signal | Value |
|--------|-------|
| Downloads | ~179M/month (top 200 PyPI package) |
| Last release | May 2021 (v2.4.0) |
| Last commit | October 2022 |
| Maintainers | 1 (Grant Jenks) |
| Open issues | 26 |
| Open PRs | 9 (unmerged) |
| Stars | 3.9K |
| Funding | Open Collective (minimal) |
| Tested Python versions | 3.7–3.12 only |

## Architecture

### Core Data Structures

The library uses a B-tree-like internal structure: a list-of-lists where each sublist maintains a bounded size. This gives O(log n) insertion/deletion and O(1) indexed access amortized.

#### 1. `SortedList`
- Maintains elements in sorted order using a segmented list structure (list-of-lists)
- Supports `add`, `discard`, `remove`, `__contains__`, `__getitem__`, `__delitem__`, `bisect_left`, `bisect_right`, `irange`, `islice`, `index`, `count`
- Custom key function support via `SortedKeyList`
- All standard sequence protocol methods

#### 2. `SortedDict`
- Subclass of `dict` with keys maintained in a `SortedList`
- Supports `peekitem(index)`, `popitem(index)`, `iloc` indexing, `irange`, `bisect_left`, `bisect_right`
- `keys()`, `values()`, `items()` return sorted views
- Custom key function support via `SortedKeysView`

#### 3. `SortedSet`
- Backed by both a `set` (for O(1) membership) and a `SortedList` (for ordering)
- Supports all set operations (`|`, `&`, `-`, `^`) returning `SortedSet`
- Supports `irange`, `islice`, `bisect_left`, `bisect_right`, `__getitem__`

### Internal Design

- **Segmented storage:** Elements stored in sublists of bounded size (load factor ~1000). This avoids O(n) insert/delete of a flat list while keeping cache-friendly access.
- **Index tree:** An optional Fenwick-tree or prefix-sum array for O(log n) positional indexing.
- **Key functions:** `SortedKeyList` stores `(key(val), val)` pairs or maintains a parallel key list for ordering.

## Improvements Over sortedcontainers

1. **Modern Python support:** Python 3.10+ only. Use `match` statements, `|` union types, `__slots__`, walrus operator where beneficial.
2. **Type annotations:** Full `py.typed` support with generic types (`SortedList[T]`, `SortedDict[K, V]`, `SortedSet[T]`).
3. **Python 3.13/3.14 compatibility:** Verified against latest CPython.
4. **Performance optimizations:** Profile and optimize hot paths.
5. **Modern packaging:** `pyproject.toml`, `src/` layout, GitHub Actions CI.
6. **Address open issues:** Resolve the 26 open issues from the original project where applicable.

## API Compatibility

SortSmith should provide a near-identical API to `sortedcontainers` to ease migration:

```python
from sortsmith import SortedList, SortedDict, SortedSet

sl = SortedList([3, 1, 2])  # SortedList([1, 2, 3])
sd = SortedDict({"b": 2, "a": 1})  # SortedDict({'a': 1, 'b': 2})
ss = SortedSet([3, 1, 2])  # SortedSet([1, 2, 3])
```

Migration guide: `s/from sortedcontainers/from sortsmith/g`

## Project Structure

```
projects/sortsmith/
  src/sortsmith/
    __init__.py          # Public API exports
    _sortedlist.py       # SortedList, SortedKeyList
    _sorteddict.py       # SortedDict
    _sortedset.py        # SortedSet
    py.typed             # PEP 561 marker
  tests/
    test_sortedlist.py
    test_sorteddict.py
    test_sortedset.py
    test_compat.py       # sortedcontainers compatibility tests
  pyproject.toml
  README.md
  LICENSE
  CHANGELOG.md
```

## Deliverables

1. `SortedList` with full API compatibility
2. `SortedDict` with full API compatibility
3. `SortedSet` with full API compatibility
4. `SortedKeyList` for custom key functions
5. Comprehensive test suite (>95% coverage)
6. Type stubs / inline types
7. Benchmarks comparing against sortedcontainers
8. README with migration guide
9. Published to PyPI as `sortsmith`

## Non-Goals

- C extensions or Cython — keep it pure Python
- Python 2 or <3.10 support
- Thread safety beyond what Python's GIL provides

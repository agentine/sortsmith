# collate

[![CI](https://github.com/agentine/collate/actions/workflows/ci.yml/badge.svg)](https://github.com/agentine/collate/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/collate)](https://pypi.org/project/collate/)
[![Python](https://img.shields.io/pypi/pyversions/collate)](https://pypi.org/project/collate/)

Pure-Python sorted containers — `SortedList`, `SortedDict`, `SortedSet`.

Drop-in replacement for [sortedcontainers](https://github.com/grantjenks/python-sortedcontainers) with full type annotations, Python 3.10+ support, and modern packaging.

## Installation

```bash
pip install collate
```

## Quick Start

```python
from collate import SortedList, SortedDict, SortedSet

sl = SortedList([3, 1, 2])    # SortedList([1, 2, 3])
sd = SortedDict(b=2, a=1)     # SortedDict({'a': 1, 'b': 2})
ss = SortedSet([3, 1, 2])     # SortedSet([1, 2, 3])
```

## Migration from sortedcontainers

```python
# Before
from sortedcontainers import SortedList, SortedDict, SortedSet

# After
from collate import SortedList, SortedDict, SortedSet
```

## License

Apache-2.0

"""Benchmarks: sortsmith.SortedDict vs sortedcontainers.SortedDict."""

from __future__ import annotations

import random
import string
import timeit
from typing import Any

HAS_SC = True
try:
    import sortedcontainers  # noqa: F401
except ImportError:
    HAS_SC = False


def rand_keys(n: int) -> list[str]:
    rng = random.Random(42)
    return ["".join(rng.choices(string.ascii_lowercase, k=8)) for _ in range(n)]


def bench(label: str, sortsmith_fn: Any, sc_fn: Any | None, number: int = 3) -> None:
    c_time = timeit.timeit(sortsmith_fn, number=number)
    if sc_fn is not None:
        s_time = timeit.timeit(sc_fn, number=number)
        ratio = c_time / s_time if s_time > 0 else float("inf")
        print(f"  {label:40s}  sortsmith={c_time:.4f}s  sc={s_time:.4f}s  ratio={ratio:.2f}x")
    else:
        print(f"  {label:40s}  sortsmith={c_time:.4f}s  sc=N/A")


def run_benchmarks() -> None:
    from sortsmith import SortedDict as CDict

    SCDict: type | None = None
    if HAS_SC:
        from sortedcontainers import SortedDict as SCDict  # type: ignore[no-redef]

    for n in [1000, 10_000]:
        print(f"\n--- N = {n} ---")
        keys = rand_keys(n)
        data = {k: i for i, k in enumerate(keys)}

        # __setitem__
        def setitem_c(d: dict[str, int] = data) -> None:
            sd = CDict()
            for k, v in d.items():
                sd[k] = v

        def setitem_s(d: dict[str, int] = data) -> None:
            sd = SCDict()  # type: ignore[misc]
            for k, v in d.items():
                sd[k] = v

        bench(f"__setitem__ {n}", setitem_c, setitem_s if HAS_SC else None)

        # Build dicts
        c_dict = CDict(data)
        sc_dict = SCDict(data) if HAS_SC else None  # type: ignore[misc]

        # keys() iteration
        def keys_c(sd: Any = c_dict) -> None:
            list(sd.keys())

        def keys_s(sd: Any = sc_dict) -> None:
            list(sd.keys())

        bench("keys() iteration", keys_c, keys_s if HAS_SC else None, number=100)

        # peekitem
        def peek_c(sd: Any = c_dict) -> None:
            for i in range(100):
                sd.peekitem(0)
                sd.peekitem(-1)

        def peek_s(sd: Any = sc_dict) -> None:
            for i in range(100):
                sd.peekitem(0)
                sd.peekitem(-1)

        bench("peekitem (200 calls)", peek_c, peek_s if HAS_SC else None, number=10)

        # __contains__
        lookup = random.sample(keys, min(1000, n))

        def contains_c(sd: Any = c_dict, ks: list[str] = lookup) -> None:
            for k in ks:
                k in sd

        def contains_s(sd: Any = sc_dict, ks: list[str] = lookup) -> None:
            for k in ks:
                k in sd

        bench("__contains__ (1000)", contains_c, contains_s if HAS_SC else None, number=10)


if __name__ == "__main__":
    print("SortedDict Benchmarks: sortsmith vs sortedcontainers")
    print("=" * 70)
    run_benchmarks()

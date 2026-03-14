"""Benchmarks: sortsmith.SortedSet vs sortedcontainers.SortedSet."""

from __future__ import annotations

import random
import timeit
from typing import Any

HAS_SC = True
try:
    import sortedcontainers  # noqa: F401
except ImportError:
    HAS_SC = False


def bench(label: str, sortsmith_fn: Any, sc_fn: Any | None, number: int = 3) -> None:
    c_time = timeit.timeit(sortsmith_fn, number=number)
    if sc_fn is not None:
        s_time = timeit.timeit(sc_fn, number=number)
        ratio = c_time / s_time if s_time > 0 else float("inf")
        print(f"  {label:40s}  sortsmith={c_time:.4f}s  sc={s_time:.4f}s  ratio={ratio:.2f}x")
    else:
        print(f"  {label:40s}  sortsmith={c_time:.4f}s  sc=N/A")


def run_benchmarks() -> None:
    from sortsmith import SortedSet as CSet

    SCSet: type | None = None
    if HAS_SC:
        from sortedcontainers import SortedSet as SCSet  # type: ignore[no-redef]

    for n in [1000, 10_000, 100_000]:
        print(f"\n--- N = {n} ---")
        data = random.sample(range(n * 10), n)

        # add() N elements
        def add_c(d: list[int] = data) -> None:
            ss = CSet()
            for v in d:
                ss.add(v)

        def add_s(d: list[int] = data) -> None:
            ss = SCSet()  # type: ignore[misc]
            for v in d:
                ss.add(v)

        bench(f"add() {n} elements", add_c, add_s if HAS_SC else None)

        # Build sets
        c_set = CSet(data)
        sc_set = SCSet(data) if HAS_SC else None  # type: ignore[misc]

        # __contains__
        targets = random.sample(data, min(1000, n))

        def contains_c(ss: Any = c_set, t: list[int] = targets) -> None:
            for v in t:
                v in ss

        def contains_s(ss: Any = sc_set, t: list[int] = targets) -> None:
            for v in t:
                v in ss

        bench("__contains__ (1000)", contains_c, contains_s if HAS_SC else None, number=100)

        # Set union
        other = random.sample(range(n * 10), n // 2)
        c_other = CSet(other)
        sc_other = SCSet(other) if HAS_SC else None  # type: ignore[misc]

        def union_c() -> None:
            c_set | c_other

        def union_s() -> None:
            sc_set | sc_other  # type: ignore[operator]

        bench("union", union_c, union_s if HAS_SC else None, number=10)

        # irange
        lo, hi = sorted(random.sample(range(n * 10), 2))

        def irange_c(ss: Any = c_set) -> None:
            list(ss.irange(lo, hi))

        def irange_s(ss: Any = sc_set) -> None:
            list(ss.irange(lo, hi))

        bench(f"irange({lo},{hi})", irange_c, irange_s if HAS_SC else None, number=10)


if __name__ == "__main__":
    print("SortedSet Benchmarks: sortsmith vs sortedcontainers")
    print("=" * 70)
    run_benchmarks()

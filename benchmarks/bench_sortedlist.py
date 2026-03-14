"""Benchmarks: sortsmith.SortedList vs sortedcontainers.SortedList."""

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
    from sortsmith import SortedList as CList

    SCList: type | None = None
    if HAS_SC:
        from sortedcontainers import SortedList as SCList  # type: ignore[no-redef]

    for n in [1000, 10_000, 100_000]:
        print(f"\n--- N = {n} ---")
        data = random.sample(range(n * 10), n)
        random.shuffle(data)

        # add() N elements
        def add_sortsmith(d: list[int] = data) -> None:
            sl = CList()
            for v in d:
                sl.add(v)

        def add_sc(d: list[int] = data) -> None:
            sl = SCList()  # type: ignore[misc]
            for v in d:
                sl.add(v)

        bench(f"add() {n} elements", add_sortsmith, add_sc if HAS_SC else None)

        # Build lists for lookup benchmarks
        c_list = CList(data)
        sc_list = SCList(data) if HAS_SC else None  # type: ignore[misc]
        targets = random.sample(data, min(1000, n))
        misses = [n * 10 + i for i in range(1000)]

        # __contains__ (hit)
        def contains_hit_c(sl: Any = c_list, t: list[int] = targets) -> None:
            for v in t:
                v in sl

        def contains_hit_s(sl: Any = sc_list, t: list[int] = targets) -> None:
            for v in t:
                v in sl

        bench("__contains__ (hit, 1000)", contains_hit_c, contains_hit_s if HAS_SC else None, number=10)

        # __contains__ (miss)
        def contains_miss_c(sl: Any = c_list, t: list[int] = misses) -> None:
            for v in t:
                v in sl

        def contains_miss_s(sl: Any = sc_list, t: list[int] = misses) -> None:
            for v in t:
                v in sl

        bench("__contains__ (miss, 1000)", contains_miss_c, contains_miss_s if HAS_SC else None, number=10)

        # __getitem__ by index
        indices = random.sample(range(n), min(1000, n))

        def getitem_c(sl: Any = c_list, idx: list[int] = indices) -> None:
            for i in idx:
                sl[i]

        def getitem_s(sl: Any = sc_list, idx: list[int] = indices) -> None:
            for i in idx:
                sl[i]

        bench("__getitem__ (1000)", getitem_c, getitem_s if HAS_SC else None, number=10)

        # bisect_left
        def bisect_c(sl: Any = c_list, t: list[int] = targets) -> None:
            for v in t:
                sl.bisect_left(v)

        def bisect_s(sl: Any = sc_list, t: list[int] = targets) -> None:
            for v in t:
                sl.bisect_left(v)

        bench("bisect_left (1000)", bisect_c, bisect_s if HAS_SC else None, number=10)

        # irange
        lo, hi = sorted(random.sample(range(n * 10), 2))

        def irange_c(sl: Any = c_list) -> None:
            list(sl.irange(lo, hi))

        def irange_s(sl: Any = sc_list) -> None:
            list(sl.irange(lo, hi))

        bench(f"irange({lo},{hi})", irange_c, irange_s if HAS_SC else None, number=10)

        # Bulk update()
        extra = random.sample(range(n * 10), n // 10)

        def update_c(d: list[int] = extra) -> None:
            sl = CList(data)
            sl.update(d)

        def update_s(d: list[int] = extra) -> None:
            sl = SCList(data)  # type: ignore[misc]
            sl.update(d)

        bench(f"update({n // 10} elements)", update_c, update_s if HAS_SC else None)


if __name__ == "__main__":
    print("SortedList Benchmarks: sortsmith vs sortedcontainers")
    print("=" * 70)
    run_benchmarks()

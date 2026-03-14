"""Tests for migration compatibility with sortedcontainers."""

from __future__ import annotations

import pytest

sc = pytest.importorskip("sortedcontainers")

from sortsmith import SortedDict, SortedList, SortedSet  # noqa: E402


class TestSortedListCompat:
    def test_basic_sorted(self) -> None:
        data = [5, 3, 1, 4, 2]
        ours = SortedList(data)
        theirs = sc.SortedList(data)
        assert list(ours) == list(theirs)

    def test_add(self) -> None:
        ours = SortedList([1, 3, 5])
        theirs = sc.SortedList([1, 3, 5])
        ours.add(2)
        theirs.add(2)
        assert list(ours) == list(theirs)

    def test_bisect(self) -> None:
        data = [1, 2, 2, 3]
        ours = SortedList(data)
        theirs = sc.SortedList(data)
        assert ours.bisect_left(2) == theirs.bisect_left(2)
        assert ours.bisect_right(2) == theirs.bisect_right(2)

    def test_count(self) -> None:
        data = [1, 2, 2, 3, 2]
        ours = SortedList(data)
        theirs = sc.SortedList(data)
        assert ours.count(2) == theirs.count(2)

    def test_index(self) -> None:
        data = [10, 20, 30, 40]
        ours = SortedList(data)
        theirs = sc.SortedList(data)
        assert ours.index(30) == theirs.index(30)

    def test_irange(self) -> None:
        data = list(range(10))
        ours = SortedList(data)
        theirs = sc.SortedList(data)
        assert list(ours.irange(3, 7)) == list(theirs.irange(3, 7))

    def test_pop(self) -> None:
        data = [1, 2, 3, 4, 5]
        ours = SortedList(data)
        theirs = sc.SortedList(data)
        assert ours.pop() == theirs.pop()
        assert ours.pop(0) == theirs.pop(0)
        assert list(ours) == list(theirs)


class TestSortedDictCompat:
    def test_keys_sorted(self) -> None:
        data = {"c": 3, "a": 1, "b": 2}
        ours = SortedDict(data)
        theirs = sc.SortedDict(data)
        assert list(ours.keys()) == list(theirs.keys())

    def test_values_sorted(self) -> None:
        data = {"c": 3, "a": 1, "b": 2}
        ours = SortedDict(data)
        theirs = sc.SortedDict(data)
        assert list(ours.values()) == list(theirs.values())

    def test_peekitem(self) -> None:
        data = {"c": 3, "a": 1, "b": 2}
        ours = SortedDict(data)
        theirs = sc.SortedDict(data)
        assert ours.peekitem(0) == theirs.peekitem(0)
        assert ours.peekitem(-1) == theirs.peekitem(-1)

    def test_popitem(self) -> None:
        data = {"c": 3, "a": 1, "b": 2}
        ours = SortedDict(data)
        theirs = sc.SortedDict(data)
        assert ours.popitem(-1) == theirs.popitem(-1)


class TestSortedSetCompat:
    def test_basic_sorted(self) -> None:
        data = [3, 1, 4, 1, 5, 9]
        ours = SortedSet(data)
        theirs = sc.SortedSet(data)
        assert list(ours) == list(theirs)

    def test_set_operations(self) -> None:
        a_data = [1, 2, 3, 4, 5]
        b_data = [3, 4, 5, 6, 7]
        ours_a = SortedSet(a_data)
        ours_b = SortedSet(b_data)
        theirs_a = sc.SortedSet(a_data)
        theirs_b = sc.SortedSet(b_data)
        assert list(ours_a | ours_b) == list(theirs_a | theirs_b)
        assert list(ours_a & ours_b) == list(theirs_a & theirs_b)
        assert list(ours_a - ours_b) == list(theirs_a - theirs_b)
        assert list(ours_a ^ ours_b) == list(theirs_a ^ theirs_b)

    def test_bisect(self) -> None:
        data = [1, 3, 5, 7, 9]
        ours = SortedSet(data)
        theirs = sc.SortedSet(data)
        assert ours.bisect_left(5) == theirs.bisect_left(5)
        assert ours.bisect_right(5) == theirs.bisect_right(5)

    def test_irange(self) -> None:
        data = list(range(10))
        ours = SortedSet(data)
        theirs = sc.SortedSet(data)
        assert list(ours.irange(3, 7)) == list(theirs.irange(3, 7))

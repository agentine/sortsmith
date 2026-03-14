"""Tests for SortedKeyList."""

from __future__ import annotations

import pytest

from sortsmith import SortedKeyList


class TestInit:
    def test_with_key(self) -> None:
        skl = SortedKeyList(["banana", "apple", "cherry"], key=str.lower)
        assert list(skl) == ["apple", "banana", "cherry"]

    def test_requires_key(self) -> None:
        with pytest.raises(TypeError):
            SortedKeyList([1, 2, 3])

    def test_empty(self) -> None:
        skl = SortedKeyList[int](key=abs)
        assert len(skl) == 0


class TestAdd:
    def test_add_maintains_key_order(self) -> None:
        skl = SortedKeyList[int](key=abs)
        skl.add(-3)
        skl.add(1)
        skl.add(-2)
        assert list(skl) == [1, -2, -3]

    def test_add_case_insensitive(self) -> None:
        skl = SortedKeyList(key=str.lower)
        skl.add("Banana")
        skl.add("apple")
        skl.add("Cherry")
        assert list(skl) == ["apple", "Banana", "Cherry"]


class TestRemoveDiscard:
    def test_remove(self) -> None:
        skl = SortedKeyList(["a", "b", "c"], key=str.lower)
        skl.remove("b")
        assert list(skl) == ["a", "c"]

    def test_remove_not_found(self) -> None:
        skl = SortedKeyList(["a"], key=str.lower)
        with pytest.raises(ValueError):
            skl.remove("z")

    def test_discard(self) -> None:
        skl = SortedKeyList(["a", "b"], key=str.lower)
        skl.discard("b")
        assert list(skl) == ["a"]

    def test_discard_not_found(self) -> None:
        skl = SortedKeyList(["a"], key=str.lower)
        skl.discard("z")  # no-op
        assert list(skl) == ["a"]


class TestContains:
    def test_contains(self) -> None:
        skl = SortedKeyList(["a", "b", "c"], key=str.lower)
        assert "b" in skl
        assert "z" not in skl


class TestBisect:
    def test_bisect_key_left(self) -> None:
        skl = SortedKeyList([-3, -2, -1, 0, 1, 2, 3], key=abs)
        # keys are [0, 1, 1, 2, 2, 3, 3]
        assert skl.bisect_key_left(2) == 3

    def test_bisect_key_right(self) -> None:
        skl = SortedKeyList([-3, -2, -1, 0, 1, 2, 3], key=abs)
        # keys are [0, 1, 1, 2, 2, 3, 3]
        assert skl.bisect_key_right(2) == 5


class TestIrangeKey:
    def test_irange_key(self) -> None:
        skl = SortedKeyList([-5, -3, -1, 0, 2, 4], key=abs)
        result = list(skl.irange_key(1, 3))
        assert result == [-1, 2, -3]

    def test_irange_key_reverse(self) -> None:
        skl = SortedKeyList([-5, -3, -1, 0, 2, 4], key=abs)
        result = list(skl.irange_key(1, 3, reverse=True))
        assert result == [-3, 2, -1]

    def test_irange_key_exclusive(self) -> None:
        skl = SortedKeyList([1, 2, 3, 4, 5], key=lambda x: x)
        result = list(skl.irange_key(2, 4, inclusive=(False, False)))
        assert result == [3]


class TestIrange:
    def test_irange_uses_key(self) -> None:
        skl = SortedKeyList(["b", "a", "c"], key=str.lower)
        result = list(skl.irange("a", "b"))
        # irange uses key for comparison
        assert result == ["a", "b"]


class TestIndex:
    def test_index(self) -> None:
        skl = SortedKeyList(["a", "b", "c"], key=str.lower)
        assert skl.index("b") == 1

    def test_index_not_found(self) -> None:
        skl = SortedKeyList(["a", "b"], key=str.lower)
        with pytest.raises(ValueError):
            skl.index("z")


class TestCount:
    def test_count(self) -> None:
        skl = SortedKeyList([-2, 2, -2], key=abs)
        # Elements with same key but different values
        assert skl.count(-2) == 2
        assert skl.count(2) == 1

    def test_count_zero(self) -> None:
        skl = SortedKeyList([1, 2, 3], key=abs)
        assert skl.count(99) == 0


class TestPop:
    def test_pop_last(self) -> None:
        skl = SortedKeyList([1, 2, 3], key=abs)
        assert skl.pop() == 3
        assert list(skl) == [1, 2]

    def test_pop_first(self) -> None:
        skl = SortedKeyList([1, 2, 3], key=abs)
        assert skl.pop(0) == 1


class TestGetitem:
    def test_getitem(self) -> None:
        skl = SortedKeyList(["b", "a", "c"], key=str.lower)
        assert skl[0] == "a"
        assert skl[-1] == "c"

    def test_getitem_slice(self) -> None:
        skl = SortedKeyList([3, 1, 2], key=abs)
        assert skl[0:2] == [1, 2]


class TestDelitem:
    def test_delitem(self) -> None:
        skl = SortedKeyList([1, 2, 3], key=abs)
        del skl[1]
        assert list(skl) == [1, 3]


class TestIslice:
    def test_islice(self) -> None:
        skl = SortedKeyList([5, 3, 1, 4, 2], key=abs)
        assert list(skl.islice(1, 3)) == [2, 3]


class TestRepr:
    def test_repr(self) -> None:
        skl = SortedKeyList([2, 1], key=abs)
        r = repr(skl)
        assert "SortedKeyList" in r
        assert "[1, 2]" in r


class TestCopy:
    def test_copy_independent(self) -> None:
        skl = SortedKeyList([1, 2, 3], key=abs)
        cp = skl.copy()
        cp.add(4)
        assert list(skl) == [1, 2, 3]
        assert list(cp) == [1, 2, 3, 4]


class TestKeyProperty:
    def test_key(self) -> None:
        skl = SortedKeyList[int](key=abs)
        assert skl.key is abs


class TestEquality:
    def test_eq(self) -> None:
        a = SortedKeyList([1, 2, 3], key=abs)
        b = SortedKeyList([3, 1, 2], key=abs)
        assert a == b

    def test_ne(self) -> None:
        a = SortedKeyList([1, 2], key=abs)
        b = SortedKeyList([1, 2, 3], key=abs)
        assert a != b


class TestUpdate:
    def test_update(self) -> None:
        skl = SortedKeyList([1, 3], key=abs)
        skl.update([2])
        assert list(skl) == [1, 2, 3]


class TestClear:
    def test_clear(self) -> None:
        skl = SortedKeyList([1, 2, 3], key=abs)
        skl.clear()
        assert len(skl) == 0

"""Tests for SortedSet."""

from __future__ import annotations

import pytest

from collate import SortedSet


class TestInit:
    def test_empty(self) -> None:
        ss = SortedSet()
        assert len(ss) == 0

    def test_from_iterable(self) -> None:
        ss = SortedSet([3, 1, 2])
        assert list(ss) == [1, 2, 3]

    def test_deduplicates(self) -> None:
        ss = SortedSet([1, 2, 2, 3, 3, 3])
        assert list(ss) == [1, 2, 3]
        assert len(ss) == 3


class TestAdd:
    def test_add(self) -> None:
        ss: SortedSet[int] = SortedSet()
        ss.add(3)
        ss.add(1)
        ss.add(2)
        assert list(ss) == [1, 2, 3]

    def test_add_duplicate(self) -> None:
        ss = SortedSet([1, 2])
        ss.add(1)
        assert list(ss) == [1, 2]


class TestRemoveDiscard:
    def test_discard(self) -> None:
        ss = SortedSet([1, 2, 3])
        ss.discard(2)
        assert list(ss) == [1, 3]

    def test_discard_not_found(self) -> None:
        ss = SortedSet([1, 2])
        ss.discard(99)  # no-op
        assert list(ss) == [1, 2]

    def test_remove(self) -> None:
        ss = SortedSet([1, 2, 3])
        ss.remove(2)
        assert list(ss) == [1, 3]

    def test_remove_not_found(self) -> None:
        ss = SortedSet([1, 2])
        with pytest.raises(KeyError):
            ss.remove(99)


class TestPop:
    def test_pop_last(self) -> None:
        ss = SortedSet([1, 2, 3])
        assert ss.pop() == 3
        assert list(ss) == [1, 2]

    def test_pop_first(self) -> None:
        ss = SortedSet([1, 2, 3])
        assert ss.pop(0) == 1
        assert list(ss) == [2, 3]


class TestContains:
    def test_in(self) -> None:
        ss = SortedSet([1, 2, 3])
        assert 2 in ss
        assert 99 not in ss


class TestLen:
    def test_len(self) -> None:
        assert len(SortedSet([1, 2, 3])) == 3

    def test_bool_empty(self) -> None:
        assert not SortedSet()

    def test_bool_nonempty(self) -> None:
        assert SortedSet([1])


class TestGetitem:
    def test_index(self) -> None:
        ss = SortedSet([10, 30, 20])
        assert ss[0] == 10
        assert ss[1] == 20
        assert ss[-1] == 30

    def test_slice(self) -> None:
        ss = SortedSet([10, 20, 30, 40])
        assert ss[1:3] == [20, 30]


class TestBisect:
    def test_bisect_left(self) -> None:
        ss = SortedSet([1, 3, 5])
        assert ss.bisect_left(3) == 1

    def test_bisect_right(self) -> None:
        ss = SortedSet([1, 3, 5])
        assert ss.bisect_right(3) == 2


class TestCount:
    def test_present(self) -> None:
        ss = SortedSet([1, 2, 3])
        assert ss.count(2) == 1

    def test_absent(self) -> None:
        ss = SortedSet([1, 2, 3])
        assert ss.count(99) == 0


class TestIndex:
    def test_index(self) -> None:
        ss = SortedSet([10, 20, 30])
        assert ss.index(20) == 1


class TestIrange:
    def test_irange(self) -> None:
        ss = SortedSet([1, 2, 3, 4, 5])
        assert list(ss.irange(2, 4)) == [2, 3, 4]

    def test_irange_reverse(self) -> None:
        ss = SortedSet([1, 2, 3, 4, 5])
        assert list(ss.irange(2, 4, reverse=True)) == [4, 3, 2]


class TestIslice:
    def test_islice(self) -> None:
        ss = SortedSet([10, 20, 30, 40, 50])
        assert list(ss.islice(1, 3)) == [20, 30]


class TestSetOperations:
    def test_union(self) -> None:
        a = SortedSet([1, 2, 3])
        b = SortedSet([3, 4, 5])
        c = a | b
        assert list(c) == [1, 2, 3, 4, 5]

    def test_union_with_set(self) -> None:
        a = SortedSet([1, 2])
        c = a | {2, 3}
        assert list(c) == [1, 2, 3]

    def test_ior(self) -> None:
        a = SortedSet([1, 2])
        a |= [3, 4]
        assert list(a) == [1, 2, 3, 4]

    def test_intersection(self) -> None:
        a = SortedSet([1, 2, 3])
        b = SortedSet([2, 3, 4])
        assert list(a & b) == [2, 3]

    def test_iand(self) -> None:
        a = SortedSet([1, 2, 3])
        a &= [2, 3, 4]
        assert list(a) == [2, 3]

    def test_difference(self) -> None:
        a = SortedSet([1, 2, 3])
        b = SortedSet([2, 3, 4])
        assert list(a - b) == [1]

    def test_isub(self) -> None:
        a = SortedSet([1, 2, 3])
        a -= [2]
        assert list(a) == [1, 3]

    def test_symmetric_difference(self) -> None:
        a = SortedSet([1, 2, 3])
        b = SortedSet([2, 3, 4])
        assert list(a ^ b) == [1, 4]

    def test_ixor(self) -> None:
        a = SortedSet([1, 2, 3])
        a ^= [2, 3, 4]
        assert list(a) == [1, 4]


class TestSetComparisons:
    def test_isdisjoint(self) -> None:
        a = SortedSet([1, 2])
        assert a.isdisjoint([3, 4])
        assert not a.isdisjoint([2, 3])

    def test_issubset(self) -> None:
        a = SortedSet([1, 2])
        assert a.issubset([1, 2, 3])
        assert not a.issubset([1, 3])

    def test_issuperset(self) -> None:
        a = SortedSet([1, 2, 3])
        assert a.issuperset([1, 2])
        assert not a.issuperset([1, 4])

    def test_lt(self) -> None:
        a = SortedSet([1, 2])
        b = SortedSet([1, 2, 3])
        assert a < b
        assert not b < a

    def test_le(self) -> None:
        a = SortedSet([1, 2])
        assert a <= SortedSet([1, 2])
        assert a <= SortedSet([1, 2, 3])

    def test_gt(self) -> None:
        a = SortedSet([1, 2, 3])
        b = SortedSet([1, 2])
        assert a > b

    def test_ge(self) -> None:
        a = SortedSet([1, 2])
        assert a >= SortedSet([1, 2])


class TestEquality:
    def test_eq(self) -> None:
        assert SortedSet([1, 2, 3]) == SortedSet([3, 1, 2])

    def test_eq_set(self) -> None:
        assert SortedSet([1, 2]) == {1, 2}

    def test_ne(self) -> None:
        assert SortedSet([1, 2]) != SortedSet([1, 2, 3])


class TestRepr:
    def test_repr(self) -> None:
        ss = SortedSet([3, 1, 2])
        assert repr(ss) == "SortedSet([1, 2, 3])"


class TestCopy:
    def test_copy_independent(self) -> None:
        ss = SortedSet([1, 2, 3])
        cp = ss.copy()
        cp.add(4)
        assert 4 not in ss
        assert 4 in cp


class TestReversed:
    def test_reversed(self) -> None:
        ss = SortedSet([1, 2, 3])
        assert list(reversed(ss)) == [3, 2, 1]


class TestUpdate:
    def test_update(self) -> None:
        ss = SortedSet([1, 2])
        ss.update([3, 4])
        assert list(ss) == [1, 2, 3, 4]


class TestClear:
    def test_clear(self) -> None:
        ss = SortedSet([1, 2, 3])
        ss.clear()
        assert len(ss) == 0


class TestKeyFunction:
    def test_key_ordering(self) -> None:
        ss: SortedSet[int] = SortedSet([1, 3, 2], key=lambda x: -x)
        assert list(ss) == [3, 2, 1]

    def test_key_add(self) -> None:
        ss: SortedSet[int] = SortedSet(key=lambda x: -x)
        ss.add(1)
        ss.add(3)
        ss.add(2)
        assert list(ss) == [3, 2, 1]

    def test_key_preserved_in_copy(self) -> None:
        ss: SortedSet[int] = SortedSet([1, 3, 2], key=lambda x: -x)
        ss2 = ss.copy()
        assert ss2._key is not None
        assert list(ss2) == [3, 2, 1]
        ss2.add(4)
        assert list(ss2) == [4, 3, 2, 1]

    def test_key_preserved_in_union(self) -> None:
        ss: SortedSet[int] = SortedSet([1, 3], key=lambda x: -x)
        result = ss | SortedSet([2, 4])
        assert list(result) == [4, 3, 2, 1]

    def test_key_preserved_in_intersection(self) -> None:
        ss: SortedSet[int] = SortedSet([1, 2, 3], key=lambda x: -x)
        result = ss & SortedSet([2, 3, 4])
        assert list(result) == [3, 2]

    def test_key_preserved_in_difference(self) -> None:
        ss: SortedSet[int] = SortedSet([1, 2, 3], key=lambda x: -x)
        result = ss - SortedSet([2])
        assert list(result) == [3, 1]

    def test_no_key(self) -> None:
        ss = SortedSet([3, 1, 2])
        assert ss._key is None
        assert list(ss) == [1, 2, 3]

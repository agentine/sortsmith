"""Tests for SortedList."""

from __future__ import annotations

import pytest

from sortsmith import SortedList


class TestInit:
    def test_empty(self) -> None:
        sl: SortedList[int] = SortedList()
        assert len(sl) == 0
        assert list(sl) == []

    def test_from_iterable(self) -> None:
        sl = SortedList([5, 3, 1, 4, 2])
        assert list(sl) == [1, 2, 3, 4, 5]

    def test_from_unsorted(self) -> None:
        sl = SortedList([10, 1, 5])
        assert list(sl) == [1, 5, 10]

    def test_duplicates(self) -> None:
        sl = SortedList([3, 1, 2, 1, 3])
        assert list(sl) == [1, 1, 2, 3, 3]

    def test_strings(self) -> None:
        sl = SortedList(["banana", "apple", "cherry"])
        assert list(sl) == ["apple", "banana", "cherry"]


class TestAdd:
    def test_add_single(self) -> None:
        sl = SortedList[int]()
        sl.add(5)
        assert list(sl) == [5]

    def test_add_maintains_order(self) -> None:
        sl = SortedList([1, 3, 5])
        sl.add(2)
        assert list(sl) == [1, 2, 3, 5]
        sl.add(4)
        assert list(sl) == [1, 2, 3, 4, 5]

    def test_add_duplicate(self) -> None:
        sl = SortedList([1, 2, 3])
        sl.add(2)
        assert list(sl) == [1, 2, 2, 3]

    def test_add_to_empty(self) -> None:
        sl = SortedList[int]()
        sl.add(42)
        assert list(sl) == [42]


class TestRemoveDiscard:
    def test_remove_existing(self) -> None:
        sl = SortedList([1, 2, 3])
        sl.remove(2)
        assert list(sl) == [1, 3]

    def test_remove_nonexistent_raises(self) -> None:
        sl = SortedList([1, 2, 3])
        with pytest.raises(ValueError):
            sl.remove(99)

    def test_remove_from_empty_raises(self) -> None:
        sl = SortedList[int]()
        with pytest.raises(ValueError):
            sl.remove(1)

    def test_discard_existing(self) -> None:
        sl = SortedList([1, 2, 3])
        sl.discard(2)
        assert list(sl) == [1, 3]

    def test_discard_nonexistent(self) -> None:
        sl = SortedList([1, 2, 3])
        sl.discard(99)  # no-op
        assert list(sl) == [1, 2, 3]

    def test_discard_empty(self) -> None:
        sl = SortedList[int]()
        sl.discard(1)  # no-op


class TestPop:
    def test_pop_last(self) -> None:
        sl = SortedList([1, 2, 3])
        assert sl.pop() == 3
        assert list(sl) == [1, 2]

    def test_pop_first(self) -> None:
        sl = SortedList([1, 2, 3])
        assert sl.pop(0) == 1
        assert list(sl) == [2, 3]

    def test_pop_middle(self) -> None:
        sl = SortedList([1, 2, 3])
        assert sl.pop(1) == 2
        assert list(sl) == [1, 3]

    def test_pop_negative_index(self) -> None:
        sl = SortedList([1, 2, 3])
        assert sl.pop(-2) == 2

    def test_pop_empty_raises(self) -> None:
        sl = SortedList[int]()
        with pytest.raises(IndexError):
            sl.pop()


class TestContains:
    def test_contains_true(self) -> None:
        sl = SortedList([1, 2, 3])
        assert 2 in sl

    def test_contains_false(self) -> None:
        sl = SortedList([1, 2, 3])
        assert 99 not in sl

    def test_contains_empty(self) -> None:
        sl = SortedList[int]()
        assert 1 not in sl

    def test_contains_wrong_type(self) -> None:
        sl = SortedList([1, 2, 3])
        assert "a" not in sl


class TestLen:
    def test_empty(self) -> None:
        assert len(SortedList[int]()) == 0

    def test_nonempty(self) -> None:
        assert len(SortedList([1, 2, 3])) == 3

    def test_bool_empty(self) -> None:
        assert not SortedList[int]()

    def test_bool_nonempty(self) -> None:
        assert SortedList([1])


class TestGetitem:
    def test_positive_index(self) -> None:
        sl = SortedList([10, 20, 30])
        assert sl[0] == 10
        assert sl[1] == 20
        assert sl[2] == 30

    def test_negative_index(self) -> None:
        sl = SortedList([10, 20, 30])
        assert sl[-1] == 30
        assert sl[-3] == 10

    def test_slice(self) -> None:
        sl = SortedList([10, 20, 30, 40, 50])
        assert sl[1:3] == [20, 30]
        assert sl[::2] == [10, 30, 50]

    def test_out_of_range(self) -> None:
        sl = SortedList([1])
        with pytest.raises(IndexError):
            sl[5]


class TestDelitem:
    def test_del_by_index(self) -> None:
        sl = SortedList([1, 2, 3, 4])
        del sl[1]
        assert list(sl) == [1, 3, 4]

    def test_del_by_slice(self) -> None:
        sl = SortedList([1, 2, 3, 4, 5])
        del sl[1:3]
        assert list(sl) == [1, 4, 5]

    def test_del_negative(self) -> None:
        sl = SortedList([1, 2, 3])
        del sl[-1]
        assert list(sl) == [1, 2]


class TestBisect:
    def test_bisect_left(self) -> None:
        sl = SortedList([1, 2, 2, 3])
        assert sl.bisect_left(2) == 1

    def test_bisect_right(self) -> None:
        sl = SortedList([1, 2, 2, 3])
        assert sl.bisect_right(2) == 3

    def test_bisect_empty(self) -> None:
        sl = SortedList[int]()
        assert sl.bisect_left(5) == 0
        assert sl.bisect_right(5) == 0

    def test_bisect_not_found(self) -> None:
        sl = SortedList([1, 3, 5])
        assert sl.bisect_left(4) == 2
        assert sl.bisect_right(4) == 2

    def test_bisect_alias(self) -> None:
        sl = SortedList([1, 2, 3])
        assert sl.bisect(2) == sl.bisect_right(2)

    def test_bisect_beyond_max(self) -> None:
        sl = SortedList([1, 2, 3])
        assert sl.bisect_left(99) == 3
        assert sl.bisect_right(99) == 3


class TestIndex:
    def test_index_found(self) -> None:
        sl = SortedList([10, 20, 30])
        assert sl.index(20) == 1

    def test_index_not_found(self) -> None:
        sl = SortedList([10, 20, 30])
        with pytest.raises(ValueError):
            sl.index(99)

    def test_index_with_start_stop(self) -> None:
        sl = SortedList([1, 2, 3, 4, 5])
        assert sl.index(3, 1, 4) == 2

    def test_index_out_of_range_raises(self) -> None:
        sl = SortedList([1, 2, 3])
        with pytest.raises(ValueError):
            sl.index(1, 1)  # 1 is at index 0, not in [1, ...)


class TestCount:
    def test_count_present(self) -> None:
        sl = SortedList([1, 2, 2, 3, 2])
        assert sl.count(2) == 3

    def test_count_absent(self) -> None:
        sl = SortedList([1, 2, 3])
        assert sl.count(99) == 0

    def test_count_single(self) -> None:
        sl = SortedList([1, 2, 3])
        assert sl.count(2) == 1


class TestIrange:
    def test_inclusive(self) -> None:
        sl = SortedList([1, 2, 3, 4, 5])
        assert list(sl.irange(2, 4)) == [2, 3, 4]

    def test_exclusive(self) -> None:
        sl = SortedList([1, 2, 3, 4, 5])
        assert list(sl.irange(2, 4, inclusive=(False, False))) == [3]

    def test_no_min(self) -> None:
        sl = SortedList([1, 2, 3, 4, 5])
        assert list(sl.irange(maximum=3)) == [1, 2, 3]

    def test_no_max(self) -> None:
        sl = SortedList([1, 2, 3, 4, 5])
        assert list(sl.irange(minimum=3)) == [3, 4, 5]

    def test_reverse(self) -> None:
        sl = SortedList([1, 2, 3, 4, 5])
        assert list(sl.irange(2, 4, reverse=True)) == [4, 3, 2]

    def test_empty_range(self) -> None:
        sl = SortedList([1, 2, 3])
        assert list(sl.irange(10, 20)) == []


class TestIslice:
    def test_basic(self) -> None:
        sl = SortedList([10, 20, 30, 40, 50])
        assert list(sl.islice(1, 3)) == [20, 30]

    def test_reverse(self) -> None:
        sl = SortedList([10, 20, 30, 40, 50])
        assert list(sl.islice(1, 4, reverse=True)) == [40, 30, 20]

    def test_no_args(self) -> None:
        sl = SortedList([1, 2, 3])
        assert list(sl.islice()) == [1, 2, 3]


class TestUpdate:
    def test_update_empty(self) -> None:
        sl = SortedList([1, 2, 3])
        sl.update([])
        assert list(sl) == [1, 2, 3]

    def test_update_adds(self) -> None:
        sl = SortedList([1, 3, 5])
        sl.update([2, 4])
        assert list(sl) == [1, 2, 3, 4, 5]


class TestClear:
    def test_clear(self) -> None:
        sl = SortedList([1, 2, 3])
        sl.clear()
        assert len(sl) == 0
        assert list(sl) == []


class TestOperators:
    def test_add(self) -> None:
        a = SortedList([1, 3])
        b = SortedList([2, 4])
        c = a + b
        assert list(c) == [1, 2, 3, 4]

    def test_iadd(self) -> None:
        sl = SortedList([1, 3])
        sl += [2, 4]
        assert list(sl) == [1, 2, 3, 4]

    def test_mul(self) -> None:
        sl = SortedList([1, 2])
        result = sl * 3
        assert list(result) == [1, 1, 1, 2, 2, 2]

    def test_imul(self) -> None:
        sl = SortedList([1, 2])
        sl *= 2
        assert list(sl) == [1, 1, 2, 2]

    def test_imul_zero(self) -> None:
        sl = SortedList([1, 2])
        sl *= 0
        assert list(sl) == []


class TestComparison:
    def test_eq(self) -> None:
        assert SortedList([1, 2, 3]) == SortedList([1, 2, 3])

    def test_ne(self) -> None:
        assert SortedList([1, 2]) != SortedList([1, 2, 3])

    def test_lt(self) -> None:
        assert SortedList([1, 2]) < SortedList([1, 2, 3])

    def test_le(self) -> None:
        assert SortedList([1, 2]) <= SortedList([1, 2])

    def test_gt(self) -> None:
        assert SortedList([1, 2, 3]) > SortedList([1, 2])

    def test_ge(self) -> None:
        assert SortedList([1, 2]) >= SortedList([1, 2])


class TestRepr:
    def test_repr(self) -> None:
        sl = SortedList([3, 1, 2])
        assert repr(sl) == "SortedList([1, 2, 3])"


class TestCopy:
    def test_copy_independent(self) -> None:
        sl = SortedList([1, 2, 3])
        cp = sl.copy()
        cp.add(4)
        assert list(sl) == [1, 2, 3]
        assert list(cp) == [1, 2, 3, 4]


class TestReversed:
    def test_reversed(self) -> None:
        sl = SortedList([1, 2, 3])
        assert list(reversed(sl)) == [3, 2, 1]


class TestIter:
    def test_iter(self) -> None:
        sl = SortedList([3, 1, 2])
        assert list(iter(sl)) == [1, 2, 3]


class TestLargeDataset:
    def test_large(self) -> None:
        import random
        data = random.sample(range(10000), 5000)
        sl = SortedList(data)
        assert list(sl) == sorted(data)
        assert len(sl) == 5000
        assert sl[0] == min(data)
        assert sl[-1] == max(data)

    def test_many_adds(self) -> None:
        sl = SortedList[int]()
        for i in range(1000):
            sl.add(i)
        assert list(sl) == list(range(1000))

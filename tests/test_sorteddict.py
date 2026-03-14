"""Tests for SortedDict."""

from __future__ import annotations

import pytest

from sortsmith import SortedDict


class TestInit:
    def test_empty(self) -> None:
        sd: SortedDict[str, int] = SortedDict()
        assert len(sd) == 0

    def test_from_dict(self) -> None:
        sd: SortedDict[str, int] = SortedDict({"c": 3, "a": 1, "b": 2})
        assert list(sd.keys()) == ["a", "b", "c"]

    def test_from_kwargs(self) -> None:
        sd: SortedDict[str, int] = SortedDict(c=3, a=1, b=2)
        assert list(sd.keys()) == ["a", "b", "c"]


class TestSetitem:
    def test_set_new_key(self) -> None:
        sd: SortedDict[str, int] = SortedDict()
        sd["b"] = 2
        sd["a"] = 1
        assert list(sd.keys()) == ["a", "b"]

    def test_set_existing_key(self) -> None:
        sd = SortedDict({"a": 1, "b": 2})
        sd["a"] = 10
        assert sd["a"] == 10
        assert list(sd.keys()) == ["a", "b"]
        assert len(sd) == 2


class TestDelitem:
    def test_del_key(self) -> None:
        sd = SortedDict({"a": 1, "b": 2, "c": 3})
        del sd["b"]
        assert list(sd.keys()) == ["a", "c"]
        assert "b" not in sd

    def test_del_nonexistent(self) -> None:
        sd = SortedDict({"a": 1})
        with pytest.raises(KeyError):
            del sd["z"]


class TestKeys:
    def test_sorted_order(self) -> None:
        sd = SortedDict({"c": 3, "a": 1, "b": 2})
        assert list(sd.keys()) == ["a", "b", "c"]

    def test_contains(self) -> None:
        sd = SortedDict({"a": 1, "b": 2})
        keys = sd.keys()
        assert "a" in keys
        assert "z" not in keys

    def test_len(self) -> None:
        sd = SortedDict({"a": 1, "b": 2})
        assert len(sd.keys()) == 2

    def test_reversed(self) -> None:
        sd = SortedDict({"a": 1, "b": 2, "c": 3})
        assert list(reversed(sd.keys())) == ["c", "b", "a"]


class TestValues:
    def test_sorted_by_key(self) -> None:
        sd = SortedDict({"c": 3, "a": 1, "b": 2})
        assert list(sd.values()) == [1, 2, 3]

    def test_len(self) -> None:
        sd = SortedDict({"a": 1, "b": 2})
        assert len(sd.values()) == 2

    def test_reversed(self) -> None:
        sd = SortedDict({"a": 1, "b": 2, "c": 3})
        assert list(reversed(sd.values())) == [3, 2, 1]


class TestItems:
    def test_sorted_by_key(self) -> None:
        sd = SortedDict({"c": 3, "a": 1, "b": 2})
        assert list(sd.items()) == [("a", 1), ("b", 2), ("c", 3)]

    def test_contains(self) -> None:
        sd = SortedDict({"a": 1, "b": 2})
        items = sd.items()
        assert ("a", 1) in items
        assert ("a", 99) not in items

    def test_len(self) -> None:
        sd = SortedDict({"a": 1})
        assert len(sd.items()) == 1


class TestPeekitem:
    def test_peek_first(self) -> None:
        sd = SortedDict({"c": 3, "a": 1, "b": 2})
        assert sd.peekitem(0) == ("a", 1)

    def test_peek_last(self) -> None:
        sd = SortedDict({"c": 3, "a": 1, "b": 2})
        assert sd.peekitem(-1) == ("c", 3)

    def test_peek_does_not_remove(self) -> None:
        sd = SortedDict({"a": 1})
        sd.peekitem(0)
        assert len(sd) == 1


class TestPopitem:
    def test_popitem_last(self) -> None:
        sd = SortedDict({"c": 3, "a": 1, "b": 2})
        k, v = sd.popitem(-1)
        assert (k, v) == ("c", 3)
        assert "c" not in sd

    def test_popitem_first(self) -> None:
        sd = SortedDict({"c": 3, "a": 1, "b": 2})
        k, v = sd.popitem(0)
        assert (k, v) == ("a", 1)
        assert "a" not in sd


class TestIloc:
    def test_iloc_getitem(self) -> None:
        sd = SortedDict({"c": 3, "a": 1, "b": 2})
        assert sd.iloc[0] == "a"
        assert sd.iloc[1] == "b"
        assert sd.iloc[-1] == "c"

    def test_iloc_slice(self) -> None:
        sd = SortedDict({"c": 3, "a": 1, "b": 2})
        assert sd.iloc[0:2] == ["a", "b"]

    def test_iloc_len(self) -> None:
        sd = SortedDict({"a": 1, "b": 2})
        assert len(sd.iloc) == 2


class TestIrange:
    def test_irange(self) -> None:
        sd = SortedDict({"a": 1, "b": 2, "c": 3, "d": 4})
        assert list(sd.irange("b", "c")) == ["b", "c"]


class TestBisect:
    def test_bisect_left(self) -> None:
        sd = SortedDict({"a": 1, "b": 2, "c": 3})
        assert sd.bisect_left("b") == 1

    def test_bisect_right(self) -> None:
        sd = SortedDict({"a": 1, "b": 2, "c": 3})
        assert sd.bisect_right("b") == 2


class TestPop:
    def test_pop_existing(self) -> None:
        sd = SortedDict({"a": 1, "b": 2})
        assert sd.pop("a") == 1
        assert "a" not in sd

    def test_pop_default(self) -> None:
        sd = SortedDict({"a": 1})
        assert sd.pop("z", 99) == 99


class TestUpdate:
    def test_update(self) -> None:
        sd = SortedDict({"a": 1})
        sd.update({"c": 3, "b": 2})
        assert list(sd.keys()) == ["a", "b", "c"]


class TestClear:
    def test_clear(self) -> None:
        sd = SortedDict({"a": 1, "b": 2})
        sd.clear()
        assert len(sd) == 0
        assert list(sd.keys()) == []


class TestSetdefault:
    def test_setdefault_new(self) -> None:
        sd: SortedDict[str, int] = SortedDict()
        sd.setdefault("a", 1)
        assert sd["a"] == 1

    def test_setdefault_existing(self) -> None:
        sd = SortedDict({"a": 1})
        sd.setdefault("a", 99)
        assert sd["a"] == 1


class TestRepr:
    def test_repr(self) -> None:
        sd = SortedDict({"b": 2, "a": 1})
        r = repr(sd)
        assert "SortedDict" in r
        assert "'a': 1" in r


class TestCopy:
    def test_copy_independent(self) -> None:
        sd = SortedDict({"a": 1, "b": 2})
        cp = sd.copy()
        cp["c"] = 3
        assert "c" not in sd
        assert "c" in cp


class TestOr:
    def test_or(self) -> None:
        a = SortedDict({"a": 1})
        b: dict[str, int] = {"b": 2}
        c = a | b
        assert list(c.keys()) == ["a", "b"]

    def test_ior(self) -> None:
        sd = SortedDict({"a": 1})
        sd |= {"b": 2}
        assert list(sd.keys()) == ["a", "b"]


class TestEquality:
    def test_eq_dict(self) -> None:
        sd = SortedDict({"a": 1, "b": 2})
        assert sd == {"a": 1, "b": 2}

    def test_ne_dict(self) -> None:
        sd = SortedDict({"a": 1})
        assert sd != {"a": 1, "b": 2}


class TestIterReversed:
    def test_iter_returns_sorted_keys(self) -> None:
        sd = SortedDict({"c": 3, "a": 1, "b": 2})
        assert list(sd) == ["a", "b", "c"]

    def test_iter_matches_keys_view(self) -> None:
        sd = SortedDict({"c": 3, "a": 1, "b": 2})
        assert list(sd) == list(sd.keys())

    def test_reversed_returns_sorted_keys(self) -> None:
        sd = SortedDict({"c": 3, "a": 1, "b": 2})
        assert list(reversed(sd)) == ["c", "b", "a"]

    def test_iter_with_key_function(self) -> None:
        sd: SortedDict[int, str] = SortedDict(lambda k: -k, {1: "a", 3: "c", 2: "b"})
        assert list(sd) == [3, 2, 1]
        assert list(sd) == list(sd.keys())

    def test_reversed_with_key_function(self) -> None:
        sd: SortedDict[int, str] = SortedDict(lambda k: -k, {1: "a", 3: "c", 2: "b"})
        assert list(reversed(sd)) == [1, 2, 3]

    def test_for_loop_uses_sorted_order(self) -> None:
        sd = SortedDict({"c": 3, "a": 1, "b": 2})
        collected = [k for k in sd]
        assert collected == ["a", "b", "c"]


class TestKeyFunction:
    def test_key_function_ordering(self) -> None:
        sd: SortedDict[int, str] = SortedDict(lambda k: -k, {1: "a", 3: "c", 2: "b"})
        assert list(sd.keys()) == [3, 2, 1]

    def test_key_function_setitem(self) -> None:
        sd: SortedDict[int, str] = SortedDict(lambda k: -k)
        sd[1] = "a"
        sd[3] = "c"
        sd[2] = "b"
        assert list(sd.keys()) == [3, 2, 1]

    def test_key_property(self) -> None:
        key_fn = lambda k: -k
        sd: SortedDict[int, str] = SortedDict(key_fn, {1: "a"})
        assert sd.key is key_fn

    def test_no_key_property(self) -> None:
        sd: SortedDict[str, int] = SortedDict({"a": 1})
        assert sd.key is None

    def test_copy_preserves_key(self) -> None:
        sd: SortedDict[int, str] = SortedDict(lambda k: -k, {1: "a", 3: "c", 2: "b"})
        sd2 = sd.copy()
        assert sd2.key is not None
        assert list(sd2.keys()) == [3, 2, 1]
        sd2[4] = "d"
        assert list(sd2.keys()) == [4, 3, 2, 1]

    def test_copy_without_key(self) -> None:
        sd = SortedDict({"c": 3, "a": 1})
        sd2 = sd.copy()
        assert sd2.key is None
        assert list(sd2.keys()) == ["a", "c"]

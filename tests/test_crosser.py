import pytest
from fieldwire.crosser import Crosser, CrossError
from fieldwire.schema import Schema, FieldSchema


def make_schema(*names: str) -> Schema:
    return Schema(fields=[FieldSchema(name=n, type=str, nullable=False) for n in names])


# ---------------------------------------------------------------------------
# Construction guards
# ---------------------------------------------------------------------------

def test_empty_prefixes_raises():
    with pytest.raises(CrossError):
        Crosser(left_prefix="", right_prefix="")


# ---------------------------------------------------------------------------
# Basic cross product
# ---------------------------------------------------------------------------

def test_cross_basic_count():
    left = [{"a": 1}, {"a": 2}]
    right = [{"b": "x"}, {"b": "y"}, {"b": "z"}]
    result = Crosser().apply(left, right)
    assert len(result) == 6


def test_cross_basic_values():
    left = [{"a": 1}]
    right = [{"b": "x"}, {"b": "y"}]
    result = Crosser().apply(left, right)
    assert result[0] == {"a": 1, "b": "x"}
    assert result[1] == {"a": 1, "b": "y"}


def test_cross_empty_left_returns_empty():
    result = Crosser().apply([], [{"b": 1}])
    assert result == []


def test_cross_empty_right_returns_empty():
    result = Crosser().apply([{"a": 1}], [])
    assert result == []


# ---------------------------------------------------------------------------
# Collision handling
# ---------------------------------------------------------------------------

def test_cross_collision_prefixes_applied():
    left = [{"id": 1, "val": "a"}]
    right = [{"id": 2, "score": 0.9}]
    result = Crosser(left_prefix="l_", right_prefix="r_").apply(left, right)
    assert len(result) == 1
    row = result[0]
    assert "l_id" in row
    assert "r_id" in row
    assert row["l_id"] == 1
    assert row["r_id"] == 2
    assert row["val"] == "a"
    assert row["score"] == 0.9


def test_cross_no_collision_no_prefix():
    left = [{"x": 10}]
    right = [{"y": 20}]
    result = Crosser().apply(left, right)
    assert result[0] == {"x": 10, "y": 20}


# ---------------------------------------------------------------------------
# Schema-driven collision detection
# ---------------------------------------------------------------------------

def test_cross_schema_collision_uses_prefix():
    ls = make_schema("name", "age")
    rs = make_schema("name", "city")
    left = [{"name": "Alice", "age": 30}]
    right = [{"name": "Bob", "city": "NYC"}]
    result = Crosser(left_schema=ls, right_schema=rs).apply(left, right)
    row = result[0]
    assert "left_name" in row
    assert "right_name" in row
    assert row["age"] == 30
    assert row["city"] == "NYC"


def test_cross_does_not_mutate_originals():
    left = [{"a": 1}]
    right = [{"b": 2}]
    left_copy = [{"a": 1}]
    right_copy = [{"b": 2}]
    Crosser().apply(left, right)
    assert left == left_copy
    assert right == right_copy


def test_cross_three_by_three():
    left = [{"x": i} for i in range(3)]
    right = [{"y": j} for j in range(3)]
    result = Crosser().apply(left, right)
    assert len(result) == 9
    xs = [r["x"] for r in result]
    ys = [r["y"] for r in result]
    assert sorted(set(xs)) == [0, 1, 2]
    assert sorted(set(ys)) == [0, 1, 2]

import pytest
from fieldwire.zipper import Zipper, ZipError
from fieldwire.schema import Schema, FieldSchema


def make_schema(*names):
    return Schema(fields=[FieldSchema(name=n, type=int, nullable=False) for n in names])


def test_zip_basic_merges_rows():
    z = Zipper()
    left = [{"a": 1}, {"a": 2}]
    right = [{"b": 10}, {"b": 20}]
    result = z.apply(left, right)
    assert result == [{"a": 1, "b": 10}, {"a": 2, "b": 20}]


def test_zip_three_lists():
    z = Zipper()
    a = [{"x": 1}]
    b = [{"y": 2}]
    c = [{"z": 3}]
    result = z.apply(a, b, c)
    assert result == [{"x": 1, "y": 2, "z": 3}]


def test_zip_unequal_lengths_pads_with_none():
    z = Zipper()
    left = [{"a": 1}, {"a": 2}, {"a": 3}]
    right = [{"b": 10}]
    result = z.apply(left, right)
    assert len(result) == 3
    assert result[0] == {"a": 1, "b": 10}
    assert result[1] == {"a": 2}
    assert result[2] == {"a": 3}


def test_zip_fill_value_used_with_schemas():
    s1 = make_schema("a")
    s2 = make_schema("b")
    z = Zipper(schemas=[s1, s2], fill_value=0)
    left = [{"a": 1}, {"a": 2}]
    right = [{"b": 10}]
    result = z.apply(left, right)
    assert result[1] == {"a": 2, "b": 0}


def test_zip_overlapping_fields_raises():
    z = Zipper()
    left = [{"a": 1}]
    right = [{"a": 99}]
    with pytest.raises(ZipError, match="Overlapping"):
        z.apply(left, right)


def test_zip_overlapping_schemas_raises_on_init():
    s1 = make_schema("a", "b")
    s2 = make_schema("b", "c")
    with pytest.raises(ZipError, match="overlapping field names"):
        Zipper(schemas=[s1, s2])


def test_zip_single_schema_list_raises_on_init():
    s1 = make_schema("a")
    with pytest.raises(ZipError, match="At least two schemas"):
        Zipper(schemas=[s1])


def test_zip_requires_at_least_two_lists():
    z = Zipper()
    with pytest.raises(ZipError, match="at least two record lists"):
        z.apply([{"a": 1}])


def test_zip_does_not_mutate_originals():
    z = Zipper()
    left = [{"a": 1}]
    right = [{"b": 2}]
    _ = z.apply(left, right)
    assert left == [{"a": 1}]
    assert right == [{"b": 2}]


def test_zip_empty_lists_returns_empty():
    z = Zipper()
    result = z.apply([], [])
    assert result == []


def test_zipper_repr():
    z = Zipper(fill_value=None)
    assert "Zipper" in repr(z)
    assert "fill_value" in repr(z)

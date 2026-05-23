import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.selector import Selector, SelectError


def make_schema(*names_types):
    fields = [FieldSchema(name=n, type=t, nullable=False) for n, t in names_types]
    return Schema(fields=fields)


# --- construction errors ---

def test_empty_fields_raises():
    with pytest.raises(SelectError, match="empty"):
        Selector(fields=[])


def test_duplicate_fields_raises():
    with pytest.raises(SelectError, match="duplicates"):
        Selector(fields=["a", "a"])


def test_unknown_field_in_schema_raises():
    schema = make_schema(("x", int), ("y", int))
    with pytest.raises(SelectError, match="not found in schema"):
        Selector(fields=["z"], schema=schema)


def test_unknown_alias_source_raises():
    schema = make_schema(("x", int))
    with pytest.raises(SelectError, match="alias source"):
        Selector(fields=["x"], schema=schema, aliases={"ghost": "renamed"})


# --- apply ---

def test_select_basic_subset():
    records = [{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]
    sel = Selector(fields=["a", "c"])
    result = sel.apply(records)
    assert result == [{"a": 1, "c": 3}, {"a": 4, "c": 6}]


def test_select_preserves_order():
    records = [{"a": 1, "b": 2, "c": 3}]
    sel = Selector(fields=["c", "a"])
    result = sel.apply(records)
    assert list(result[0].keys()) == ["c", "a"]


def test_select_does_not_mutate_original():
    records = [{"a": 1, "b": 2}]
    sel = Selector(fields=["a"])
    sel.apply(records)
    assert "b" in records[0]


def test_select_with_alias():
    records = [{"name": "alice", "age": 30}]
    sel = Selector(fields=["name", "age"], aliases={"name": "full_name"})
    result = sel.apply(records)
    assert result == [{"full_name": "alice", "age": 30}]


def test_select_missing_field_in_record_raises():
    records = [{"a": 1}]  # missing 'b'
    sel = Selector(fields=["a", "b"])
    with pytest.raises(SelectError, match="missing from record"):
        sel.apply(records)


def test_select_empty_records_returns_empty():
    sel = Selector(fields=["x"])
    assert sel.apply([]) == []


# --- output_schema ---

def test_output_schema_none_when_no_schema():
    sel = Selector(fields=["a"])
    assert sel.output_schema() is None


def test_output_schema_correct_fields():
    schema = make_schema(("a", int), ("b", str), ("c", float))
    sel = Selector(fields=["a", "c"], schema=schema)
    out = sel.output_schema()
    assert out is not None
    names = [f.name for f in out.fields]
    assert names == ["a", "c"]


def test_output_schema_with_alias():
    schema = make_schema(("score", float), ("label", str))
    sel = Selector(fields=["score", "label"], schema=schema, aliases={"score": "value"})
    out = sel.output_schema()
    names = [f.name for f in out.fields]
    assert names == ["value", "label"]


# --- repr ---

def test_repr_contains_fields():
    sel = Selector(fields=["x", "y"])
    assert "x" in repr(sel)
    assert "y" in repr(sel)

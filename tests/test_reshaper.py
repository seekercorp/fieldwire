import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.reshaper import Reshaper, ReshapeError


def make_schema(*names: str) -> Schema:
    return Schema(fields=[FieldSchema(name=n, type=int, nullable=False) for n in names])


# ---------------------------------------------------------------------------
# Construction errors
# ---------------------------------------------------------------------------

def test_empty_fields_raises():
    with pytest.raises(ReshapeError, match="empty"):
        Reshaper(fields=[])


def test_duplicate_fields_raises():
    with pytest.raises(ReshapeError, match="duplicate"):
        Reshaper(fields=["a", "a"])


def test_unknown_field_in_schema_raises():
    schema = make_schema("x", "y")
    with pytest.raises(ReshapeError, match="not found in schema"):
        Reshaper(fields=["x", "z"], schema=schema)


# ---------------------------------------------------------------------------
# Basic reshaping
# ---------------------------------------------------------------------------

def test_reshape_reorders_fields():
    records = [{"a": 1, "b": 2, "c": 3}]
    r = Reshaper(fields=["c", "a"])
    result = r.apply(records)
    assert result == [{"c": 3, "a": 1}]
    assert list(result[0].keys()) == ["c", "a"]


def test_reshape_selects_subset():
    records = [{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]
    r = Reshaper(fields=["b"])
    result = r.apply(records)
    assert result == [{"b": 2}, {"b": 5}]


def test_reshape_does_not_mutate_original():
    records = [{"a": 1, "b": 2}]
    r = Reshaper(fields=["a"])
    r.apply(records)
    assert "b" in records[0]


def test_reshape_empty_records_returns_empty():
    r = Reshaper(fields=["a"])
    assert r.apply([]) == []


# ---------------------------------------------------------------------------
# Missing field handling
# ---------------------------------------------------------------------------

def test_missing_field_raises_by_default():
    records = [{"a": 1}]
    r = Reshaper(fields=["a", "b"])
    with pytest.raises(ReshapeError, match="missing field 'b'"):
        r.apply(records)


def test_fill_missing_inserts_none():
    records = [{"a": 1}]
    r = Reshaper(fields=["a", "b"], fill_missing=True)
    result = r.apply(records)
    assert result == [{"a": 1, "b": None}]


# ---------------------------------------------------------------------------
# output_schema
# ---------------------------------------------------------------------------

def test_output_schema_none_when_no_schema():
    r = Reshaper(fields=["a", "b"])
    assert r.output_schema() is None


def test_output_schema_contains_selected_fields_in_order():
    schema = make_schema("a", "b", "c")
    r = Reshaper(fields=["c", "a"], schema=schema)
    out = r.output_schema()
    assert out is not None
    names = [f.name for f in out.fields]
    assert names == ["c", "a"]


def test_output_schema_preserves_field_types():
    schema = Schema(fields=[
        FieldSchema(name="x", type=str, nullable=False),
        FieldSchema(name="y", type=float, nullable=True),
    ])
    r = Reshaper(fields=["y", "x"], schema=schema)
    out = r.output_schema()
    assert out is not None
    assert out.fields[0].type == float
    assert out.fields[1].type == str

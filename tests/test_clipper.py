import pytest

from fieldwire.clipper import Clipper, ClipError
from fieldwire.schema import Schema, FieldSchema


def make_schema(*fields):
    return Schema(fields=list(fields))


# ---------------------------------------------------------------------------
# Construction guards
# ---------------------------------------------------------------------------

def test_empty_bounds_raises():
    with pytest.raises(ClipError, match="bounds must not be empty"):
        Clipper(bounds={})


def test_inverted_bounds_raises():
    with pytest.raises(ClipError, match="lower bound"):
        Clipper(bounds={"x": (10.0, 5.0)})


def test_schema_unknown_field_raises():
    schema = make_schema(FieldSchema("value", float, nullable=False))
    with pytest.raises(ClipError, match="not found in schema"):
        Clipper(bounds={"missing": (0.0, 1.0)}, schema=schema)


# ---------------------------------------------------------------------------
# Basic clipping
# ---------------------------------------------------------------------------

def test_clip_lower_bound():
    clipper = Clipper(bounds={"x": (0.0, None)})
    records = [{"x": -5.0}, {"x": 3.0}]
    result = clipper.apply(records)
    assert result[0]["x"] == 0.0
    assert result[1]["x"] == 3.0


def test_clip_upper_bound():
    clipper = Clipper(bounds={"x": (None, 100.0)})
    records = [{"x": 200.0}, {"x": 50.0}]
    result = clipper.apply(records)
    assert result[0]["x"] == 100.0
    assert result[1]["x"] == 50.0


def test_clip_both_bounds():
    clipper = Clipper(bounds={"score": (0.0, 1.0)})
    records = [{"score": -0.5}, {"score": 0.5}, {"score": 1.5}]
    result = clipper.apply(records)
    assert result[0]["score"] == 0.0
    assert result[1]["score"] == 0.5
    assert result[2]["score"] == 1.0


def test_clip_integer_values():
    clipper = Clipper(bounds={"n": (1, 10)})
    records = [{"n": 0}, {"n": 5}, {"n": 20}]
    result = clipper.apply(records)
    assert [r["n"] for r in result] == [1, 5, 10]


def test_clip_none_value_skipped():
    clipper = Clipper(bounds={"x": (0.0, 10.0)})
    records = [{"x": None}]
    result = clipper.apply(records)
    assert result[0]["x"] is None


def test_clip_does_not_mutate_original():
    clipper = Clipper(bounds={"x": (0.0, 5.0)})
    original = [{"x": 99.0}]
    _ = clipper.apply(original)
    assert original[0]["x"] == 99.0


def test_clip_multiple_fields():
    clipper = Clipper(bounds={"a": (0, 10), "b": (-1.0, 1.0)})
    records = [{"a": 15, "b": 2.0, "c": "keep"}]
    result = clipper.apply(records)
    assert result[0]["a"] == 10
    assert result[0]["b"] == 1.0
    assert result[0]["c"] == "keep"


def test_clip_non_numeric_raises():
    clipper = Clipper(bounds={"x": (0.0, 10.0)})
    with pytest.raises(ClipError, match="non-numeric"):
        clipper.apply([{"x": "oops"}])


def test_clip_empty_records_returns_empty():
    clipper = Clipper(bounds={"x": (0.0, 1.0)})
    assert clipper.apply([]) == []


def test_clip_with_schema_validates_field():
    schema = make_schema(
        FieldSchema("score", float, nullable=True),
    )
    clipper = Clipper(bounds={"score": (0.0, 1.0)}, schema=schema)
    records = [{"score": 1.8}]
    result = clipper.apply(records)
    assert result[0]["score"] == 1.0

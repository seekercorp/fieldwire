"""Tests for fieldwire.inference module."""

import pytest
from fieldwire.inference import infer_field_schema, infer_schema
from fieldwire.schema import FieldSchema, Schema


# --- infer_field_schema ---

def test_infer_field_int():
    field = infer_field_schema("age", [1, 2, 3])
    assert field.name == "age"
    assert field.dtype == int
    assert field.nullable is False


def test_infer_field_float():
    field = infer_field_schema("score", [1.0, 2.5, 3.7])
    assert field.dtype == float
    assert field.nullable is False


def test_infer_field_str():
    field = infer_field_schema("label", ["a", "b", "c"])
    assert field.dtype == str


def test_infer_field_nullable():
    field = infer_field_schema("value", [1, None, 3])
    assert field.dtype == int
    assert field.nullable is True


def test_infer_field_all_none():
    field = infer_field_schema("unknown", [None, None])
    assert field.nullable is True
    assert field.dtype == str


def test_infer_field_int_and_float_promotes_to_float():
    field = infer_field_schema("mixed_num", [1, 2.5, 3])
    assert field.dtype == float


def test_infer_field_mixed_types_falls_back_to_str():
    field = infer_field_schema("chaos", [1, "hello", True])
    assert field.dtype == str


# --- infer_schema ---

def test_infer_schema_basic():
    records = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
    ]
    schema = infer_schema(records, schema_name="people")
    assert isinstance(schema, Schema)
    assert schema.name == "people"
    assert len(schema.fields) == 2


def test_infer_schema_field_types():
    records = [
        {"x": 1.0, "label": "cat"},
        {"x": 2.0, "label": "dog"},
    ]
    schema = infer_schema(records)
    field_map = {f.name: f for f in schema.fields}
    assert field_map["x"].dtype == float
    assert field_map["label"].dtype == str


def test_infer_schema_with_missing_keys():
    records = [
        {"a": 1, "b": "hello"},
        {"a": 2},
    ]
    schema = infer_schema(records)
    field_map = {f.name: f for f in schema.fields}
    assert field_map["b"].nullable is True


def test_infer_schema_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        infer_schema([])


def test_infer_schema_default_name():
    records = [{"val": 42}]
    schema = infer_schema(records)
    assert schema.name == "inferred"

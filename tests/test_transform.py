"""Tests for fieldwire.transform module."""

import pytest
from fieldwire.transform import FieldTransform, Transformer, TransformError
from fieldwire.schema import Schema, FieldSchema


# --- Helpers ---

def make_schema(*fields):
    return Schema(fields=list(fields))


INT_SCHEMA = make_schema(
    FieldSchema(name="value", type=int, nullable=False),
    FieldSchema(name="label", type=str, nullable=False),
)

OUT_SCHEMA = make_schema(
    FieldSchema(name="value", type=int, nullable=False),
    FieldSchema(name="label", type=str, nullable=False),
    FieldSchema(name="doubled", type=int, nullable=False),
)


# --- FieldTransform tests ---

def test_field_transform_applies_fn():
    t = FieldTransform(field="value", fn=lambda x: x * 2)
    result = t.apply({"value": 5, "label": "a"})
    assert result["value"] == 10
    assert result["label"] == "a"


def test_field_transform_does_not_mutate_original():
    original = {"value": 3}
    t = FieldTransform(field="value", fn=lambda x: x + 1)
    result = t.apply(original)
    assert original["value"] == 3
    assert result["value"] == 4


def test_field_transform_missing_field_raises():
    t = FieldTransform(field="missing", fn=lambda x: x)
    with pytest.raises(TransformError, match="not found"):
        t.apply({"value": 1})


def test_field_transform_fn_exception_raises():
    t = FieldTransform(field="value", fn=lambda x: x / 0, description="div_zero")
    with pytest.raises(TransformError, match="div_zero"):
        t.apply({"value": 5})


def test_field_transform_repr():
    t = FieldTransform(field="x", fn=lambda x: x, description="noop")
    assert "noop" in repr(t)
    assert "x" in repr(t)


# --- Transformer tests ---

def test_transformer_basic():
    t = Transformer(transforms=[FieldTransform("value", lambda x: x + 1)])
    result = t.run({"value": 10, "label": "test"})
    assert result["value"] == 11


def test_transformer_run_batch():
    t = Transformer(transforms=[FieldTransform("value", lambda x: x * 3)])
    records = [{"value": 1}, {"value": 2}, {"value": 3}]
    results = t.run_batch(records)
    assert [r["value"] for r in results] == [3, 6, 9]


def test_transformer_input_schema_valid():
    t = Transformer(
        transforms=[FieldTransform("value", lambda x: x + 1)],
        input_schema=INT_SCHEMA,
    )
    result = t.run({"value": 5, "label": "ok"})
    assert result["value"] == 6


def test_transformer_input_schema_invalid_raises():
    t = Transformer(
        transforms=[FieldTransform("value", lambda x: x + 1)],
        input_schema=INT_SCHEMA,
    )
    with pytest.raises(TransformError, match="Input validation failed"):
        t.run({"value": "not_an_int", "label": "bad"})


def test_transformer_output_schema_invalid_raises():
    # Transform produces wrong type
    t = Transformer(
        transforms=[FieldTransform("value", lambda x: str(x))],
        output_schema=INT_SCHEMA,
    )
    with pytest.raises(TransformError, match="Output validation failed"):
        t.run({"value": 5, "label": "ok"})


def test_transformer_no_transforms_passes_through():
    t = Transformer(transforms=[])
    record = {"value": 42, "label": "x"}
    assert t.run(record) == record

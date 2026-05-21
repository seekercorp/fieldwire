"""Tests for fieldwire schema inference and validation."""

import pytest
from fieldwire.schema import FieldSchema, Schema, infer_schema


class TestFieldSchema:
    def test_validate_correct_type(self):
        fs = FieldSchema(name="age", dtype="integer")
        assert fs.validate(42) is True

    def test_validate_wrong_type(self):
        fs = FieldSchema(name="age", dtype="integer")
        assert fs.validate("not an int") is False

    def test_validate_none_not_nullable(self):
        fs = FieldSchema(name="name", dtype="string", nullable=False)
        assert fs.validate(None) is False

    def test_validate_none_nullable(self):
        fs = FieldSchema(name="name", dtype="string", nullable=True)
        assert fs.validate(None) is True

    def test_validate_unknown_dtype_passes(self):
        fs = FieldSchema(name="data", dtype="unknown")
        assert fs.validate({"any": "value"}) is True


class TestSchema:
    def test_field_names(self):
        schema = Schema(fields=[
            FieldSchema(name="id", dtype="integer"),
            FieldSchema(name="label", dtype="string"),
        ])
        assert schema.field_names() == ["id", "label"]

    def test_get_field_found(self):
        fs = FieldSchema(name="score", dtype="float")
        schema = Schema(fields=[fs])
        assert schema.get_field("score") is fs

    def test_get_field_not_found(self):
        schema = Schema(fields=[])
        assert schema.get_field("missing") is None

    def test_validate_record_valid(self):
        schema = Schema(fields=[
            FieldSchema(name="id", dtype="integer"),
            FieldSchema(name="name", dtype="string"),
        ])
        errors = schema.validate_record({"id": 1, "name": "Alice"})
        assert errors == []

    def test_validate_record_missing_required(self):
        schema = Schema(fields=[
            FieldSchema(name="id", dtype="integer", nullable=False),
        ])
        errors = schema.validate_record({})
        assert any("Missing required field" in e for e in errors)

    def test_validate_record_type_mismatch(self):
        schema = Schema(fields=[
            FieldSchema(name="count", dtype="integer"),
        ])
        errors = schema.validate_record({"count": "oops"})
        assert any("count" in e for e in errors)

    def test_validate_record_nullable_missing_ok(self):
        schema = Schema(fields=[
            FieldSchema(name="notes", dtype="string", nullable=True),
        ])
        errors = schema.validate_record({})
        assert errors == []


class TestInferSchema:
    def test_empty_records(self):
        schema = infer_schema([])
        assert schema.fields == []

    def test_basic_inference(self):
        records = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        schema = infer_schema(records)
        id_field = schema.get_field("id")
        name_field = schema.get_field("name")
        assert id_field is not None and id_field.dtype == "integer"
        assert name_field is not None and name_field.dtype == "string"

    def test_nullable_inference(self):
        records = [{"val": 1}, {"val": None}]
        schema = infer_schema(records)
        val_field = schema.get_field("val")
        assert val_field is not None and val_field.nullable is True

    def test_mixed_types(self):
        records = [{"x": 1}, {"x": "hello"}]
        schema = infer_schema(records)
        x_field = schema.get_field("x")
        assert x_field is not None and x_field.dtype == "mixed"

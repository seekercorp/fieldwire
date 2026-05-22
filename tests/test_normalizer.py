import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.normalizer import Normalizer, NormalizeError


def make_schema():
    return Schema(fields=[
        FieldSchema(name="x", type=float, nullable=True),
        FieldSchema(name="y", type=float, nullable=True),
        FieldSchema(name="label", type=str, nullable=False),
    ])


def test_minmax_scales_to_zero_one():
    schema = make_schema()
    norm = Normalizer(schema=schema, fields=["x"], strategy="minmax")
    records = [{"x": 0.0, "y": 1.0, "label": "a"}, {"x": 10.0, "y": 2.0, "label": "b"}]
    result = norm.apply(records)
    assert result[0]["x"] == 0.0
    assert result[1]["x"] == 1.0


def test_minmax_midpoint():
    schema = make_schema()
    norm = Normalizer(schema=schema, fields=["x"], strategy="minmax")
    records = [{"x": 0.0, "y": 0.0, "label": "a"}, {"x": 5.0, "y": 0.0, "label": "b"}, {"x": 10.0, "y": 0.0, "label": "c"}]
    result = norm.apply(records)
    assert result[1]["x"] == pytest.approx(0.5)


def test_zscore_mean_zero():
    schema = make_schema()
    norm = Normalizer(schema=schema, fields=["x"], strategy="zscore")
    records = [{"x": float(i), "y": 0.0, "label": str(i)} for i in range(5)]
    result = norm.apply(records)
    mean = sum(r["x"] for r in result) / len(result)
    assert mean == pytest.approx(0.0, abs=1e-9)


def test_zscore_constant_values_no_division_by_zero():
    schema = make_schema()
    norm = Normalizer(schema=schema, fields=["x"], strategy="zscore")
    records = [{"x": 5.0, "y": 1.0, "label": "a"}, {"x": 5.0, "y": 1.0, "label": "b"}]
    result = norm.apply(records)
    assert result[0]["x"] == pytest.approx(0.0)


def test_minmax_constant_no_division_by_zero():
    schema = make_schema()
    norm = Normalizer(schema=schema, fields=["x"], strategy="minmax")
    records = [{"x": 3.0, "y": 0.0, "label": "a"}, {"x": 3.0, "y": 0.0, "label": "b"}]
    result = norm.apply(records)
    assert result[0]["x"] == pytest.approx(0.0)


def test_normalizer_skips_none_values():
    schema = make_schema()
    norm = Normalizer(schema=schema, fields=["x"], strategy="minmax")
    records = [{"x": None, "y": 1.0, "label": "a"}, {"x": 10.0, "y": 2.0, "label": "b"}]
    result = norm.apply(records)
    assert result[0]["x"] is None


def test_normalizer_does_not_mutate_original():
    schema = make_schema()
    norm = Normalizer(schema=schema, fields=["x"], strategy="minmax")
    records = [{"x": 0.0, "y": 1.0, "label": "a"}, {"x": 10.0, "y": 2.0, "label": "b"}]
    norm.apply(records)
    assert records[0]["x"] == 0.0


def test_normalizer_multiple_fields():
    schema = make_schema()
    norm = Normalizer(schema=schema, fields=["x", "y"], strategy="minmax")
    records = [{"x": 0.0, "y": 0.0, "label": "a"}, {"x": 10.0, "y": 4.0, "label": "b"}]
    result = norm.apply(records)
    assert result[1]["x"] == 1.0
    assert result[1]["y"] == 1.0


def test_normalizer_empty_records():
    schema = make_schema()
    norm = Normalizer(schema=schema, fields=["x"], strategy="minmax")
    assert norm.apply([]) == []


def test_normalizer_invalid_strategy_raises():
    schema = make_schema()
    with pytest.raises(NormalizeError, match="Unknown strategy"):
        Normalizer(schema=schema, fields=["x"], strategy="robust")


def test_normalizer_unknown_field_raises():
    schema = make_schema()
    with pytest.raises(NormalizeError, match="not found in schema"):
        Normalizer(schema=schema, fields=["z"], strategy="minmax")


def test_normalizer_repr():
    schema = make_schema()
    norm = Normalizer(schema=schema, fields=["x"], strategy="zscore")
    assert "zscore" in repr(norm)
    assert "x" in repr(norm)

import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.filler import Filler, FillError


def make_schema():
    return Schema(fields=[
        FieldSchema(name="value", type=float, nullable=True),
        FieldSchema(name="label", type=str, nullable=True),
    ])


def test_fill_explicit_replaces_none():
    schema = make_schema()
    filler = Filler(schema=schema, fill_values={"value": 0.0, "label": "unknown"})
    records = [{"value": None, "label": None}, {"value": 1.0, "label": "a"}]
    result = filler.apply(records)
    assert result[0]["value"] == 0.0
    assert result[0]["label"] == "unknown"
    assert result[1]["value"] == 1.0


def test_fill_explicit_does_not_overwrite_non_none():
    schema = make_schema()
    filler = Filler(schema=schema, fill_values={"value": 99.0})
    records = [{"value": 5.0, "label": None}]
    result = filler.apply(records)
    assert result[0]["value"] == 5.0


def test_fill_forward_propagates_last_value():
    schema = make_schema()
    filler = Filler(schema=schema, strategy="forward")
    records = [
        {"value": 1.0, "label": "x"},
        {"value": None, "label": None},
        {"value": None, "label": "y"},
    ]
    result = filler.apply(records)
    assert result[1]["value"] == 1.0
    assert result[1]["label"] == "x"
    assert result[2]["value"] == 1.0
    assert result[2]["label"] == "y"


def test_fill_forward_no_previous_leaves_none():
    schema = make_schema()
    filler = Filler(schema=schema, strategy="forward")
    records = [{"value": None, "label": None}]
    result = filler.apply(records)
    assert result[0]["value"] is None


def test_fill_backward_propagates_next_value():
    schema = make_schema()
    filler = Filler(schema=schema, strategy="backward")
    records = [
        {"value": None, "label": None},
        {"value": 3.0, "label": "z"},
    ]
    result = filler.apply(records)
    assert result[0]["value"] == 3.0
    assert result[0]["label"] == "z"


def test_fill_mean_replaces_with_average():
    schema = make_schema()
    filler = Filler(schema=schema, strategy="mean")
    records = [
        {"value": 2.0, "label": "a"},
        {"value": None, "label": None},
        {"value": 4.0, "label": "b"},
    ]
    result = filler.apply(records)
    assert result[1]["value"] == 3.0


def test_fill_zero_replaces_none_with_zero():
    schema = make_schema()
    filler = Filler(schema=schema, strategy="zero")
    records = [{"value": None, "label": None}]
    result = filler.apply(records)
    assert result[0]["value"] == 0
    assert result[0]["label"] == 0


def test_fill_empty_records_returns_empty():
    schema = make_schema()
    filler = Filler(schema=schema, strategy="forward")
    assert filler.apply([]) == []


def test_fill_invalid_strategy_raises():
    schema = make_schema()
    with pytest.raises(FillError, match="Unknown strategy"):
        Filler(schema=schema, strategy="interpolate")


def test_fill_both_strategy_and_values_raises():
    schema = make_schema()
    with pytest.raises(FillError, match="not both"):
        Filler(schema=schema, fill_values={"value": 0.0}, strategy="zero")


def test_fill_unknown_field_in_fill_values_raises():
    schema = make_schema()
    with pytest.raises(FillError, match="not found in schema"):
        Filler(schema=schema, fill_values={"nonexistent": 0})


def test_fill_does_not_mutate_original():
    schema = make_schema()
    filler = Filler(schema=schema, fill_values={"value": 9.0})
    original = [{"value": None, "label": "a"}]
    filler.apply(original)
    assert original[0]["value"] is None


def test_filler_repr():
    schema = make_schema()
    filler = Filler(schema=schema, strategy="mean")
    assert "mean" in repr(filler)

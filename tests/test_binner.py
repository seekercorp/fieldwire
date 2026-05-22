import pytest
from fieldwire.binner import Binner, BinError
from fieldwire.schema import Schema, FieldSchema


def make_schema():
    return Schema(fields=[
        FieldSchema(name="value", type=float, nullable=False),
        FieldSchema(name="label", type=str, nullable=True),
    ])


def test_bin_basic_assignment():
    binner = Binner(field="value", bins=[10.0, 20.0], labels=["low", "mid", "high"])
    records = [{"value": 5.0}, {"value": 15.0}, {"value": 25.0}]
    result = binner.apply(records)
    assert result[0]["bin"] == "low"
    assert result[1]["bin"] == "mid"
    assert result[2]["bin"] == "high"


def test_bin_boundary_is_upper_exclusive():
    binner = Binner(field="value", bins=[10.0], labels=["low", "high"])
    records = [{"value": 10.0}]
    result = binner.apply(records)
    assert result[0]["bin"] == "high"


def test_bin_none_value_returns_none():
    binner = Binner(field="value", bins=[10.0], labels=["low", "high"])
    records = [{"value": None}]
    result = binner.apply(records)
    assert result[0]["bin"] is None


def test_bin_custom_output_field():
    binner = Binner(
        field="value", bins=[5.0], labels=["small", "large"], output_field="size"
    )
    records = [{"value": 3.0}]
    result = binner.apply(records)
    assert "size" in result[0]
    assert result[0]["size"] == "small"


def test_bin_does_not_mutate_original():
    binner = Binner(field="value", bins=[10.0], labels=["low", "high"])
    original = {"value": 5.0}
    records = [original]
    binner.apply(records)
    assert "bin" not in original


def test_bin_preserves_other_fields():
    binner = Binner(field="value", bins=[10.0], labels=["low", "high"])
    records = [{"value": 5.0, "name": "alice"}]
    result = binner.apply(records)
    assert result[0]["name"] == "alice"


def test_bin_missing_field_raises():
    binner = Binner(field="value", bins=[10.0], labels=["low", "high"])
    with pytest.raises(BinError, match="missing from record"):
        binner.apply([{"other": 1.0}])


def test_bin_wrong_label_count_raises():
    with pytest.raises(BinError, match="labels"):
        Binner(field="value", bins=[10.0, 20.0], labels=["only_one"])


def test_bin_unsorted_edges_raises():
    with pytest.raises(BinError, match="ascending"):
        Binner(field="value", bins=[20.0, 10.0], labels=["a", "b", "c"])


def test_bin_schema_field_not_found_raises():
    schema = make_schema()
    with pytest.raises(BinError, match="not found in schema"):
        Binner(field="nonexistent", bins=[10.0], labels=["low", "high"], schema=schema)


def test_bin_output_schema_adds_field():
    schema = make_schema()
    binner = Binner(
        field="value", bins=[10.0], labels=["low", "high"], schema=schema
    )
    out = binner.output_schema()
    names = [f.name for f in out.fields]
    assert "bin" in names
    bin_field = next(f for f in out.fields if f.name == "bin")
    assert bin_field.type is str
    assert bin_field.nullable is True


def test_bin_output_schema_none_when_no_schema():
    binner = Binner(field="value", bins=[10.0], labels=["low", "high"])
    assert binner.output_schema() is None


def test_bin_repr():
    binner = Binner(field="value", bins=[10.0], labels=["low", "high"])
    r = repr(binner)
    assert "Binner" in r
    assert "value" in r

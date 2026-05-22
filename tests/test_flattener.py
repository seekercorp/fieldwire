import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.flattener import Flattener, FlattenError


def make_schema(*fields):
    return Schema(fields=[FieldSchema(name=n, dtype=t, nullable=nl) for n, t, nl in fields])


# --- Basic flattening ---

def test_flatten_basic():
    schema = make_schema(("id", int, False), ("meta", dict, True))
    flattener = Flattener(schema=schema, field="meta")
    records = [{"id": 1, "meta": {"city": "NYC", "zip": "10001"}}]
    result = flattener.apply(records)
    assert result[0]["meta_city"] == "NYC"
    assert result[0]["meta_zip"] == "10001"
    assert "meta" not in result[0]


def test_flatten_removes_original_field():
    schema = make_schema(("x", int, False), ("info", dict, True))
    flattener = Flattener(schema=schema, field="info")
    result = flattener.apply([{"x": 1, "info": {"a": 2}}])
    assert "info" not in result[0]


def test_flatten_preserves_other_fields():
    schema = make_schema(("id", int, False), ("data", dict, True))
    flattener = Flattener(schema=schema, field="data")
    result = flattener.apply([{"id": 99, "data": {"k": "v"}}])
    assert result[0]["id"] == 99


# --- Custom prefix ---

def test_flatten_custom_prefix():
    schema = make_schema(("meta", dict, True))
    flattener = Flattener(schema=schema, field="meta", prefix="m")
    result = flattener.apply([{"meta": {"x": 1}}])
    assert "m_x" in result[0]


def test_flatten_custom_separator():
    schema = make_schema(("meta", dict, True))
    flattener = Flattener(schema=schema, field="meta", separator=".")
    result = flattener.apply([{"meta": {"val": 5}}])
    assert "meta.val" in result[0]


# --- Null nested field ---

def test_flatten_none_nested_field():
    schema = make_schema(("id", int, False), ("meta", dict, True))
    flattener = Flattener(schema=schema, field="meta")
    result = flattener.apply([{"id": 1, "meta": None}])
    assert result[0] == {"id": 1}


# --- Output schema ---

def test_output_schema_contains_flattened_fields():
    schema = make_schema(("id", int, False), ("props", dict, True))
    flattener = Flattener(schema=schema, field="props")
    sample = {"id": 1, "props": {"color": "red", "size": 10}}
    out = flattener.output_schema(sample)
    names = [f.name for f in out.fields]
    assert "props_color" in names
    assert "props_size" in names
    assert "props" not in names


def test_output_schema_flattened_fields_nullable():
    schema = make_schema(("props", dict, True))
    flattener = Flattener(schema=schema, field="props")
    sample = {"props": {"a": 1}}
    out = flattener.output_schema(sample)
    assert out.fields[0].nullable is True


# --- Error cases ---

def test_flatten_unknown_field_raises():
    schema = make_schema(("x", int, False))
    with pytest.raises(FlattenError, match="not found in schema"):
        Flattener(schema=schema, field="missing")


def test_flatten_non_dict_field_raises():
    schema = make_schema(("x", int, False))
    with pytest.raises(FlattenError, match="dtype=dict"):
        Flattener(schema=schema, field="x")


def test_flatten_non_dict_value_at_runtime_raises():
    schema = make_schema(("meta", dict, True))
    flattener = Flattener(schema=schema, field="meta")
    with pytest.raises(FlattenError, match="Expected dict"):
        flattener.apply([{"meta": "not_a_dict"}])


# --- Repr ---

def test_repr():
    schema = make_schema(("info", dict, True))
    flattener = Flattener(schema=schema, field="info")
    r = repr(flattener)
    assert "Flattener" in r
    assert "info" in r

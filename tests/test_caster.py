import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.caster import Caster, CastError


def make_schema(*fields):
    return Schema(fields=[FieldSchema(name=n, dtype=t, nullable=nl) for n, t, nl in fields])


# --- Basic casting ---

def test_cast_str_to_int():
    schema = make_schema(("value", str, False))
    caster = Caster(schema=schema, casts={"value": int})
    result = caster.apply([{"value": "42"}, {"value": "7"}])
    assert result == [{"value": 42}, {"value": 7}]


def test_cast_int_to_float():
    schema = make_schema(("score", int, False))
    caster = Caster(schema=schema, casts={"score": float})
    result = caster.apply([{"score": 3}, {"score": 5}])
    assert result == [{"score": 3.0}, {"score": 5.0}]


def test_cast_float_to_str():
    schema = make_schema(("amount", float, False))
    caster = Caster(schema=schema, casts={"amount": str})
    result = caster.apply([{"amount": 1.5}])
    assert result[0]["amount"] == "1.5"


def test_cast_int_to_bool():
    schema = make_schema(("flag", int, False))
    caster = Caster(schema=schema, casts={"flag": bool})
    result = caster.apply([{"flag": 1}, {"flag": 0}])
    assert result[0]["flag"] is True
    assert result[1]["flag"] is False


# --- Output schema ---

def test_output_schema_updated():
    schema = make_schema(("x", str, False), ("y", int, False))
    caster = Caster(schema=schema, casts={"x": int})
    out = caster.output_schema
    assert out.fields[0].dtype == int
    assert out.fields[1].dtype == int


def test_output_schema_preserves_nullable():
    schema = make_schema(("val", str, True))
    caster = Caster(schema=schema, casts={"val": float})
    out = caster.output_schema
    assert out.fields[0].nullable is True


def test_uncasted_fields_unchanged_in_output_schema():
    schema = make_schema(("a", str, False), ("b", int, False))
    caster = Caster(schema=schema, casts={"a": int})
    out = caster.output_schema
    assert out.fields[1].dtype == int
    assert out.fields[1].name == "b"


# --- Nullable handling ---

def test_cast_nullable_none_passes():
    schema = make_schema(("val", str, True))
    caster = Caster(schema=schema, casts={"val": int})
    result = caster.apply([{"val": None}])
    assert result[0]["val"] is None


def test_cast_non_nullable_none_raises():
    schema = make_schema(("val", str, False))
    caster = Caster(schema=schema, casts={"val": int})
    with pytest.raises(CastError, match="non-nullable"):
        caster.apply([{"val": None}])


# --- Error cases ---

def test_cast_unknown_field_raises():
    schema = make_schema(("x", str, False))
    with pytest.raises(CastError, match="not found in schema"):
        Caster(schema=schema, casts={"unknown": int})


def test_cast_unsupported_type_raises():
    schema = make_schema(("x", str, False))
    with pytest.raises(CastError, match="Unsupported cast target type"):
        Caster(schema=schema, casts={"x": list})


def test_cast_invalid_value_raises():
    schema = make_schema(("x", str, False))
    caster = Caster(schema=schema, casts={"x": int})
    with pytest.raises(CastError, match="Failed to cast"):
        caster.apply([{"x": "not_an_int"}])


def test_cast_invalid_value_error_includes_field_name():
    schema = make_schema(("price", str, False))
    caster = Caster(schema=schema, casts={"price": float})
    with pytest.raises(CastError, match="price"):
        caster.apply([{"price": "not_a_float"}])

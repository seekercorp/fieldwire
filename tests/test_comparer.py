import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.comparer import Comparer, CompareError, CompareResult


def make_schema():
    return Schema(fields=[
        FieldSchema(name="id", type=int, nullable=False),
        FieldSchema(name="value", type=float, nullable=True),
        FieldSchema(name="label", type=str, nullable=True),
    ])


def test_empty_fields_raises():
    schema = make_schema()
    with pytest.raises(CompareError, match="must not be empty"):
        Comparer(schema=schema, fields=[])


def test_unknown_field_raises():
    schema = make_schema()
    with pytest.raises(CompareError, match="Unknown fields"):
        Comparer(schema=schema, fields=["nonexistent"])


def test_unknown_key_raises():
    schema = make_schema()
    with pytest.raises(CompareError, match="Key field"):
        Comparer(schema=schema, key="bad_key")


def test_compare_positional_all_match():
    schema = make_schema()
    comparer = Comparer(schema=schema, fields=["value", "label"])
    left = [{"id": 1, "value": 1.0, "label": "a"}]
    right = [{"id": 1, "value": 1.0, "label": "a"}]
    results = comparer.compare(left, right)
    assert len(results) == 1
    assert results[0]["all_match"] is True


def test_compare_positional_mismatch():
    schema = make_schema()
    comparer = Comparer(schema=schema, fields=["value", "label"])
    left = [{"id": 1, "value": 1.0, "label": "a"}]
    right = [{"id": 1, "value": 2.0, "label": "a"}]
    results = comparer.compare(left, right)
    assert results[0]["all_match"] is False
    value_cmp = next(c for c in results[0]["comparisons"] if c.field == "value")
    assert value_cmp.match is False
    assert value_cmp.left_value == 1.0
    assert value_cmp.right_value == 2.0


def test_compare_positional_index():
    schema = make_schema()
    comparer = Comparer(schema=schema, fields=["value"])
    left = [{"id": 1, "value": 10.0}, {"id": 2, "value": 20.0}]
    right = [{"id": 1, "value": 10.0}, {"id": 2, "value": 99.0}]
    results = comparer.compare(left, right)
    assert results[0]["_index"] == 0
    assert results[1]["_index"] == 1
    assert results[0]["all_match"] is True
    assert results[1]["all_match"] is False


def test_compare_by_key_match():
    schema = make_schema()
    comparer = Comparer(schema=schema, fields=["value", "label"], key="id")
    left = [{"id": 1, "value": 5.0, "label": "x"}, {"id": 2, "value": 6.0, "label": "y"}]
    right = [{"id": 2, "value": 6.0, "label": "y"}, {"id": 1, "value": 5.0, "label": "x"}]
    results = comparer.compare(left, right)
    assert all(r["all_match"] for r in results)


def test_compare_by_key_missing_right():
    schema = make_schema()
    comparer = Comparer(schema=schema, fields=["value"], key="id")
    left = [{"id": 1, "value": 5.0}]
    right = []
    results = comparer.compare(left, right)
    assert results[0]["_key"] == 1
    assert results[0]["all_match"] is False


def test_compare_result_repr():
    cr = CompareResult(field="x", left_value=1, right_value=2, match=False)
    assert "CompareResult" in repr(cr)
    assert "match=False" in repr(cr)


def test_comparer_repr():
    schema = make_schema()
    comparer = Comparer(schema=schema, fields=["value"], key="id")
    r = repr(comparer)
    assert "Comparer" in r
    assert "key='id'" in r


def test_default_fields_uses_all_schema_fields():
    schema = make_schema()
    comparer = Comparer(schema=schema)
    assert set(comparer._compare_fields) == {"id", "value", "label"}

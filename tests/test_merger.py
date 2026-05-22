import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.merger import Merger, MergeError


def make_schema():
    return Schema(fields=[
        FieldSchema(name="id", type=int, nullable=False),
        FieldSchema(name="value", type=float, nullable=False),
    ])


def test_merge_two_lists():
    schema = make_schema()
    merger = Merger(schema=schema)
    a = [{"id": 1, "value": 1.0}, {"id": 2, "value": 2.0}]
    b = [{"id": 3, "value": 3.0}]
    result = merger.apply(a, b)
    assert len(result) == 3
    assert result[0]["id"] == 1
    assert result[2]["id"] == 3


def test_merge_preserves_order():
    schema = make_schema()
    merger = Merger(schema=schema)
    a = [{"id": 1, "value": 1.0}]
    b = [{"id": 2, "value": 2.0}]
    c = [{"id": 3, "value": 3.0}]
    result = merger.apply(a, b, c)
    assert [r["id"] for r in result] == [1, 2, 3]


def test_merge_no_dedup_keeps_duplicates():
    schema = make_schema()
    merger = Merger(schema=schema, deduplicate=False)
    a = [{"id": 1, "value": 1.0}]
    b = [{"id": 1, "value": 1.0}]
    result = merger.apply(a, b)
    assert len(result) == 2


def test_merge_dedup_by_key():
    schema = make_schema()
    merger = Merger(schema=schema, deduplicate=True, dedup_key="id")
    a = [{"id": 1, "value": 1.0}, {"id": 2, "value": 2.0}]
    b = [{"id": 1, "value": 99.0}, {"id": 3, "value": 3.0}]
    result = merger.apply(a, b)
    assert len(result) == 3
    ids = [r["id"] for r in result]
    assert ids.count(1) == 1


def test_merge_dedup_no_key_uses_full_record():
    schema = make_schema()
    merger = Merger(schema=schema, deduplicate=True)
    a = [{"id": 1, "value": 1.0}]
    b = [{"id": 1, "value": 1.0}, {"id": 2, "value": 2.0}]
    result = merger.apply(a, b)
    assert len(result) == 2


def test_merge_empty_lists():
    schema = make_schema()
    merger = Merger(schema=schema)
    result = merger.apply([], [])
    assert result == []


def test_merge_invalid_dedup_key_raises():
    schema = make_schema()
    with pytest.raises(MergeError, match="dedup_key"):
        Merger(schema=schema, deduplicate=True, dedup_key="nonexistent")


def test_merge_repr():
    schema = make_schema()
    merger = Merger(schema=schema, deduplicate=True, dedup_key="id")
    r = repr(merger)
    assert "deduplicate=True" in r
    assert "id" in r

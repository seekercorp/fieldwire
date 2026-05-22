import pytest
from fieldwire.deduplicator import Deduplicator, DeduplicateError
from fieldwire.schema import Schema, FieldSchema


def make_schema(*names_types):
    fields = [FieldSchema(name=n, dtype=t, nullable=False) for n, t in names_types]
    return Schema(fields=fields)


def test_dedup_keep_first_removes_duplicates():
    records = [
        {"id": 1, "val": "a"},
        {"id": 2, "val": "b"},
        {"id": 1, "val": "c"},
    ]
    d = Deduplicator(keys=["id"])
    result = d.apply(records)
    assert len(result) == 2
    assert result[0] == {"id": 1, "val": "a"}
    assert result[1] == {"id": 2, "val": "b"}


def test_dedup_keep_last():
    records = [
        {"id": 1, "val": "a"},
        {"id": 1, "val": "c"},
        {"id": 2, "val": "b"},
    ]
    d = Deduplicator(keys=["id"], keep="last")
    result = d.apply(records)
    assert len(result) == 2
    assert result[0] == {"id": 1, "val": "c"}


def test_dedup_composite_key():
    records = [
        {"a": 1, "b": 1, "v": 10},
        {"a": 1, "b": 2, "v": 20},
        {"a": 1, "b": 1, "v": 30},
    ]
    d = Deduplicator(keys=["a", "b"])
    result = d.apply(records)
    assert len(result) == 2


def test_dedup_no_duplicates_returns_all():
    records = [{"id": i} for i in range(5)]
    d = Deduplicator(keys=["id"])
    result = d.apply(records)
    assert len(result) == 5


def test_dedup_empty_input_returns_empty():
    d = Deduplicator(keys=["id"])
    assert d.apply([]) == []


def test_dedup_with_valid_schema():
    schema = make_schema(("id", int), ("val", str))
    records = [{"id": 1, "val": "x"}, {"id": 1, "val": "y"}]
    d = Deduplicator(keys=["id"])
    result = d.apply(records, schema=schema)
    assert len(result) == 1


def test_dedup_schema_missing_key_raises():
    schema = make_schema(("id", int),)
    records = [{"id": 1}]
    d = Deduplicator(keys=["missing"])
    with pytest.raises(DeduplicateError, match="not found in schema"):
        d.apply(records, schema=schema)


def test_dedup_record_missing_key_raises():
    records = [{"id": 1}, {"val": "no_id"}]
    d = Deduplicator(keys=["id"])
    with pytest.raises(DeduplicateError, match="missing key field"):
        d.apply(records)


def test_dedup_empty_keys_raises():
    with pytest.raises(DeduplicateError, match="At least one key"):
        Deduplicator(keys=[])


def test_dedup_invalid_keep_raises():
    with pytest.raises(DeduplicateError, match="'keep' must be"):
        Deduplicator(keys=["id"], keep="middle")


def test_dedup_repr():
    d = Deduplicator(keys=["id", "name"], keep="last")
    assert "Deduplicator" in repr(d)
    assert "id" in repr(d)
    assert "last" in repr(d)

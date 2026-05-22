import hashlib
import pytest

from fieldwire.hasher import Hasher, HashError
from fieldwire.schema import Schema, FieldSchema


def make_schema(*names: str) -> Schema:
    return Schema(fields=[FieldSchema(name=n, type=str, nullable=False) for n in names])


def _expected(fields, values, algorithm="md5"):
    parts = "|".join(f"{f}={v}" for f, v in zip(fields, values))
    return hashlib.new(algorithm, parts.encode()).hexdigest()


def test_hash_single_field_default_md5():
    h = Hasher(fields=["id"])
    records = [{"id": 1, "name": "alice"}]
    result = h.apply(records)
    assert result[0]["_hash"] == _expected(["id"], [1])


def test_hash_composite_fields():
    h = Hasher(fields=["a", "b"])
    records = [{"a": "foo", "b": 42}]
    result = h.apply(records)
    assert result[0]["_hash"] == _expected(["a", "b"], ["foo", 42])


def test_hash_preserves_other_fields():
    h = Hasher(fields=["x"])
    records = [{"x": 10, "y": 20}]
    result = h.apply(records)
    assert result[0]["x"] == 10
    assert result[0]["y"] == 20


def test_hash_does_not_mutate_original():
    h = Hasher(fields=["id"])
    original = [{"id": 5}]
    h.apply(original)
    assert "_hash" not in original[0]


def test_hash_custom_output_field():
    h = Hasher(fields=["id"], output_field="row_hash")
    result = h.apply([{"id": 99}])
    assert "row_hash" in result[0]
    assert "_hash" not in result[0]


def test_hash_sha256_algorithm():
    h = Hasher(fields=["val"], algorithm="sha256")
    records = [{"val": "hello"}]
    result = h.apply(records)
    assert result[0]["_hash"] == _expected(["val"], ["hello"], algorithm="sha256")


def test_hash_sha1_algorithm():
    h = Hasher(fields=["val"], algorithm="sha1")
    records = [{"val": "test"}]
    result = h.apply(records)
    assert result[0]["_hash"] == _expected(["val"], ["test"], algorithm="sha1")


def test_hash_empty_fields_raises():
    with pytest.raises(HashError, match="fields must not be empty"):
        Hasher(fields=[])


def test_hash_unsupported_algorithm_raises():
    with pytest.raises(HashError, match="Unsupported algorithm"):
        Hasher(fields=["id"], algorithm="crc32")


def test_hash_schema_validates_field_names():
    schema = make_schema("id", "name")
    with pytest.raises(HashError, match="missing"):
        Hasher(fields=["nonexistent"], schema=schema)


def test_hash_schema_valid_passes():
    schema = make_schema("id", "name")
    h = Hasher(fields=["id", "name"], schema=schema)
    result = h.apply([{"id": 1, "name": "bob"}])
    assert "_hash" in result[0]


def test_hash_missing_field_in_record_raises():
    h = Hasher(fields=["id"])
    with pytest.raises(HashError, match="missing from record"):
        h.apply([{"name": "alice"}])


def test_hash_multiple_records_independent():
    h = Hasher(fields=["id"])
    records = [{"id": 1}, {"id": 2}]
    result = h.apply(records)
    assert result[0]["_hash"] != result[1]["_hash"]
    assert result[0]["_hash"] == _expected(["id"], [1])
    assert result[1]["_hash"] == _expected(["id"], [2])

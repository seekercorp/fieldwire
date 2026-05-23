import pytest
from fieldwire.truncator import Truncator, TruncateError
from fieldwire.schema import Schema, FieldSchema


def make_schema(*fields):
    return Schema([FieldSchema(name=n, type=t, nullable=True) for n, t in fields])


# --- construction errors ---

def test_negative_max_length_raises():
    with pytest.raises(TruncateError, match="max_length must be non-negative"):
        Truncator(fields=["name"], max_length=-1)


def test_empty_fields_raises():
    with pytest.raises(TruncateError, match="fields must not be empty"):
        Truncator(fields=[], max_length=10)


def test_unknown_field_in_schema_raises():
    schema = make_schema(("name", str))
    with pytest.raises(TruncateError, match="not found in schema"):
        Truncator(fields=["missing"], max_length=5, schema=schema)


def test_non_str_field_in_schema_raises():
    schema = make_schema(("age", int))
    with pytest.raises(TruncateError, match="must be of type str"):
        Truncator(fields=["age"], max_length=5, schema=schema)


# --- basic truncation ---

def test_truncate_basic():
    t = Truncator(fields=["name"], max_length=5)
    records = [{"name": "Alexander"}]
    result = t.apply(records)
    assert result[0]["name"] == "Alexa"


def test_truncate_no_change_when_short_enough():
    t = Truncator(fields=["name"], max_length=10)
    records = [{"name": "Alice"}]
    result = t.apply(records)
    assert result[0]["name"] == "Alice"


def test_truncate_with_suffix():
    t = Truncator(fields=["title"], max_length=8, suffix="...")
    records = [{"title": "Hello World"}]
    result = t.apply(records)
    assert result[0]["title"] == "Hello..."
    assert len(result[0]["title"]) == 8


def test_truncate_suffix_longer_than_max_length_truncates_to_empty():
    t = Truncator(fields=["text"], max_length=2, suffix="...")
    records = [{"text": "Hello"}]
    result = t.apply(records)
    # cut = max(0, 2-3) = 0, so result is just suffix trimmed
    assert result[0]["text"] == "..."


def test_truncate_none_value_is_left_unchanged():
    t = Truncator(fields=["name"], max_length=5)
    records = [{"name": None}]
    result = t.apply(records)
    assert result[0]["name"] is None


def test_truncate_multiple_fields():
    t = Truncator(fields=["first", "last"], max_length=3)
    records = [{"first": "Jonathan", "last": "Smith", "age": 30}]
    result = t.apply(records)
    assert result[0]["first"] == "Jon"
    assert result[0]["last"] == "Smi"
    assert result[0]["age"] == 30


def test_truncate_does_not_mutate_original():
    t = Truncator(fields=["name"], max_length=3)
    original = {"name": "Alexander"}
    records = [original]
    t.apply(records)
    assert original["name"] == "Alexander"


def test_truncate_non_str_runtime_raises():
    t = Truncator(fields=["value"], max_length=5)
    records = [{"value": 12345}]
    with pytest.raises(TruncateError, match="Expected str"):
        t.apply(records)


def test_truncate_empty_records_returns_empty():
    t = Truncator(fields=["name"], max_length=5)
    assert t.apply([]) == []


def test_truncate_zero_max_length():
    t = Truncator(fields=["name"], max_length=0)
    records = [{"name": "Alice"}]
    result = t.apply(records)
    assert result[0]["name"] == ""

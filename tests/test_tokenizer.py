import pytest

from fieldwire.schema import FieldSchema, Schema
from fieldwire.tokenizer import Tokenizer, TokenizeError


def make_schema(*fields):
    return Schema(fields=list(fields))


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def test_unknown_input_field_raises():
    schema = make_schema(FieldSchema(name="text", dtype=str, nullable=False))
    with pytest.raises(TokenizeError, match="Input field 'missing'"):
        Tokenizer(input_field="missing", output_field="tokens", schema=schema)


def test_non_str_input_field_raises():
    schema = make_schema(FieldSchema(name="value", dtype=int, nullable=False))
    with pytest.raises(TokenizeError, match="must be of type str"):
        Tokenizer(input_field="value", output_field="tokens", schema=schema)


def test_output_field_already_exists_raises():
    schema = make_schema(
        FieldSchema(name="text", dtype=str, nullable=False),
        FieldSchema(name="tokens", dtype=str, nullable=True),
    )
    with pytest.raises(TokenizeError, match="already exists"):
        Tokenizer(input_field="text", output_field="tokens", schema=schema)


# ---------------------------------------------------------------------------
# Basic functionality
# ---------------------------------------------------------------------------

def test_tokenize_basic_splits_on_whitespace():
    t = Tokenizer(input_field="text", output_field="tokens")
    records = [{"text": "Hello World"}]
    result = t.apply(records)
    assert result[0]["tokens"] == ["hello", "world"]


def test_tokenize_preserves_other_fields():
    t = Tokenizer(input_field="text", output_field="tokens")
    records = [{"id": 1, "text": "foo bar"}]
    result = t.apply(records)
    assert result[0]["id"] == 1
    assert result[0]["text"] == "foo bar"


def test_tokenize_does_not_mutate_original():
    t = Tokenizer(input_field="text", output_field="tokens")
    original = {"text": "hello world"}
    records = [original]
    t.apply(records)
    assert "tokens" not in original


def test_tokenize_none_value_produces_none_tokens():
    t = Tokenizer(input_field="text", output_field="tokens")
    records = [{"text": None}]
    result = t.apply(records)
    assert result[0]["tokens"] is None


def test_tokenize_empty_string_returns_empty_list():
    t = Tokenizer(input_field="text", output_field="tokens")
    records = [{"text": ""}]
    result = t.apply(records)
    assert result[0]["tokens"] == []


def test_tokenize_multiple_records():
    t = Tokenizer(input_field="text", output_field="tokens")
    records = [{"text": "a b"}, {"text": "c d e"}]
    result = t.apply(records)
    assert result[0]["tokens"] == ["a", "b"]
    assert result[1]["tokens"] == ["c", "d", "e"]


# ---------------------------------------------------------------------------
# Custom tokenizer function
# ---------------------------------------------------------------------------

def test_custom_tokenize_fn():
    def comma_split(text: str):
        return [t.strip() for t in text.split(",")]

    t = Tokenizer(input_field="csv", output_field="parts", tokenize_fn=comma_split)
    records = [{"csv": "a, b, c"}]
    result = t.apply(records)
    assert result[0]["parts"] == ["a", "b", "c"]


def test_custom_tokenize_fn_exception_raises():
    def bad_fn(text: str):
        raise ValueError("boom")

    t = Tokenizer(input_field="text", output_field="tokens", tokenize_fn=bad_fn)
    with pytest.raises(TokenizeError, match="boom"):
        t.apply([{"text": "hello"}])


# ---------------------------------------------------------------------------
# Missing field in record
# ---------------------------------------------------------------------------

def test_missing_field_in_record_raises():
    t = Tokenizer(input_field="text", output_field="tokens")
    with pytest.raises(TokenizeError, match="missing field 'text'"):
        t.apply([{"other": "value"}])


def test_wrong_type_in_record_raises():
    t = Tokenizer(input_field="text", output_field="tokens")
    with pytest.raises(TokenizeError, match="Expected str"):
        t.apply([{"text": 42}])

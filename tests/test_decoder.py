import json
import pytest

from fieldwire.decoder import Decoder, DecodeError
from fieldwire.schema import Schema, FieldSchema


RECORDS = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]


def make_schema():
    return Schema(fields=[
        FieldSchema(name="id", type=int, nullable=False),
        FieldSchema(name="name", type=str, nullable=False),
    ])


def test_decode_json_basic():
    dec = Decoder(format="json")
    text = json.dumps(RECORDS)
    result = dec.decode(text)
    assert result == RECORDS


def test_decode_json_invalid_raises():
    dec = Decoder(format="json")
    with pytest.raises(DecodeError, match="Invalid JSON"):
        dec.decode("{not valid}")


def test_decode_json_non_array_raises():
    dec = Decoder(format="json")
    with pytest.raises(DecodeError, match="array"):
        dec.decode(json.dumps({"key": "value"}))


def test_decode_csv_basic():
    dec = Decoder(format="csv")
    text = "id,name\n1,Alice\n2,Bob\n"
    result = dec.decode(text)
    assert result[0]["name"] == "Alice"
    assert len(result) == 2


def test_decode_csv_custom_delimiter():
    dec = Decoder(format="csv", csv_delimiter=";")
    text = "id;name\n1;Alice\n"
    result = dec.decode(text)
    assert result[0]["id"] == "1"


def test_decode_invalid_format_raises():
    with pytest.raises(DecodeError, match="Unsupported format"):
        Decoder(format="xml")  # type: ignore[arg-type]


def test_decode_with_schema_validation_passes():
    schema = make_schema()
    dec = Decoder(format="json", schema=schema)
    text = json.dumps(RECORDS)
    result = dec.decode(text)
    assert len(result) == 2


def test_decode_with_schema_validation_fails_on_null():
    schema = make_schema()
    dec = Decoder(format="json", schema=schema)
    bad = [{"id": None, "name": "Alice"}]
    with pytest.raises(DecodeError, match="Validation failed"):
        dec.decode(json.dumps(bad))


def test_decode_empty_json_array():
    dec = Decoder(format="json")
    assert dec.decode("[]") == []

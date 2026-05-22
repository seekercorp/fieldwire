import json
import pytest

from fieldwire.encoder import Encoder, EncodeError


RECORDS = [
    {"id": 1, "name": "Alice", "score": 9.5},
    {"id": 2, "name": "Bob", "score": 7.0},
]


def test_encode_json_basic():
    enc = Encoder(format="json")
    result = enc.encode(RECORDS)
    parsed = json.loads(result)
    assert parsed == RECORDS


def test_encode_json_indent():
    enc = Encoder(format="json", indent=2)
    result = enc.encode(RECORDS)
    assert "\n" in result
    assert json.loads(result) == RECORDS


def test_encode_json_empty_list():
    enc = Encoder(format="json")
    assert enc.encode([]) == "[]"


def test_encode_csv_basic():
    enc = Encoder(format="csv")
    result = enc.encode(RECORDS)
    lines = result.strip().split("\n")
    assert lines[0] == "id,name,score"
    assert "Alice" in lines[1]
    assert "Bob" in lines[2]


def test_encode_csv_custom_delimiter():
    enc = Encoder(format="csv", csv_delimiter=";")
    result = enc.encode(RECORDS)
    assert result.startswith("id;name;score")


def test_encode_csv_empty_list():
    enc = Encoder(format="csv")
    assert enc.encode([]) == ""


def test_encode_invalid_format_raises():
    with pytest.raises(EncodeError, match="Unsupported format"):
        Encoder(format="xml")  # type: ignore[arg-type]


def test_encode_non_list_raises():
    enc = Encoder(format="json")
    with pytest.raises(EncodeError, match="list of dicts"):
        enc.encode({"bad": "input"})  # type: ignore[arg-type]


def test_encode_json_non_serialisable_falls_back_to_str():
    import datetime
    records = [{"ts": datetime.date(2024, 1, 1)}]
    enc = Encoder(format="json")
    result = json.loads(enc.encode(records))
    assert result[0]["ts"] == "2024-01-01"

import pytest
from fieldwire.expander import Expander, ExpandError
from fieldwire.schema import Schema, FieldSchema


def make_schema(*names: str) -> Schema:
    return Schema(fields=[FieldSchema(name=n, type=str, nullable=True) for n in names])


# ---------------------------------------------------------------------------
# Construction guards
# ---------------------------------------------------------------------------

def test_unknown_field_in_schema_raises():
    schema = make_schema("a", "b")
    with pytest.raises(ExpandError, match="not found in schema"):
        Expander(field="z", schema=schema)


# ---------------------------------------------------------------------------
# Basic expansion
# ---------------------------------------------------------------------------

def test_expand_basic():
    records = [{"tags": ["x", "y", "z"], "id": 1}]
    result = Expander(field="tags").apply(records)
    assert len(result) == 3
    assert [r["tags"] for r in result] == ["x", "y", "z"]
    assert all(r["id"] == 1 for r in result)


def test_expand_removes_original_list_field():
    records = [{"items": [1, 2], "name": "Alice"}]
    result = Expander(field="items").apply(records)
    for row in result:
        assert "items" in row  # output_field defaults to field name
        assert isinstance(row["items"], int)


def test_expand_custom_output_field():
    records = [{"nums": [10, 20]}]
    result = Expander(field="nums", output_field="value").apply(records)
    assert "nums" not in result[0]
    assert result[0]["value"] == 10
    assert result[1]["value"] == 20


def test_expand_multiple_rows():
    records = [
        {"id": 1, "vals": ["a", "b"]},
        {"id": 2, "vals": ["c"]},
    ]
    result = Expander(field="vals").apply(records)
    assert len(result) == 3
    assert result[0] == {"id": 1, "vals": "a"}
    assert result[1] == {"id": 1, "vals": "b"}
    assert result[2] == {"id": 2, "vals": "c"}


# ---------------------------------------------------------------------------
# keep_index flag
# ---------------------------------------------------------------------------

def test_expand_keep_index():
    records = [{"letters": ["a", "b", "c"]}]
    result = Expander(field="letters", keep_index=True).apply(records)
    assert [r["_index"] for r in result] == [0, 1, 2]


def test_expand_no_index_by_default():
    records = [{"letters": ["a"]}]
    result = Expander(field="letters").apply(records)
    assert "_index" not in result[0]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_expand_none_value_skips_row():
    records = [{"tags": None, "id": 1}, {"tags": ["x"], "id": 2}]
    result = Expander(field="tags").apply(records)
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_expand_empty_list_yields_no_rows():
    records = [{"tags": [], "id": 1}]
    result = Expander(field="tags").apply(records)
    assert result == []


def test_expand_non_list_value_raises():
    records = [{"tags": "not-a-list"}]
    with pytest.raises(ExpandError, match="Expected a list"):
        Expander(field="tags").apply(records)


def test_expand_missing_field_in_record_raises():
    records = [{"other": 1}]
    with pytest.raises(ExpandError, match="missing from record"):
        Expander(field="tags").apply(records)


def test_expand_does_not_mutate_original():
    original = [{"tags": ["a", "b"], "id": 1}]
    copy = [{"tags": ["a", "b"], "id": 1}]
    Expander(field="tags").apply(original)
    assert original == copy

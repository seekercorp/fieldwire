import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.sorter import Sorter, SortError


def make_schema():
    return Schema(
        fields=[
            FieldSchema(name="name", field_type=str, nullable=False),
            FieldSchema(name="age", field_type=int, nullable=False),
            FieldSchema(name="score", field_type=float, nullable=True),
        ]
    )


RECORDS = [
    {"name": "Charlie", "age": 30, "score": 7.5},
    {"name": "Alice", "age": 25, "score": 9.0},
    {"name": "Bob", "age": 25, "score": 6.0},
]


def test_sort_single_key_ascending():
    sorter = Sorter(make_schema(), keys=["age"])
    result = sorter.sort(RECORDS)
    ages = [r["age"] for r in result]
    assert ages == sorted(ages)


def test_sort_single_key_descending():
    sorter = Sorter(make_schema(), keys=["age"], ascending=[False])
    result = sorter.sort(RECORDS)
    ages = [r["age"] for r in result]
    assert ages == sorted(ages, reverse=True)


def test_sort_multi_key():
    sorter = Sorter(make_schema(), keys=["age", "score"], ascending=[True, False])
    result = sorter.sort(RECORDS)
    assert result[0]["name"] == "Alice"   # age=25, score=9.0
    assert result[1]["name"] == "Bob"     # age=25, score=6.0
    assert result[2]["name"] == "Charlie" # age=30


def test_sort_by_string_field():
    sorter = Sorter(make_schema(), keys=["name"])
    result = sorter.sort(RECORDS)
    names = [r["name"] for r in result]
    assert names == ["Alice", "Bob", "Charlie"]


def test_sort_empty_records():
    sorter = Sorter(make_schema(), keys=["age"])
    assert sorter.sort([]) == []


def test_sort_does_not_mutate_original():
    sorter = Sorter(make_schema(), keys=["age"])
    original = list(RECORDS)
    sorter.sort(RECORDS)
    assert RECORDS == original


def test_sort_with_none_values_last():
    records = [
        {"name": "Alice", "age": 25, "score": 9.0},
        {"name": "Bob", "age": 30, "score": None},
        {"name": "Charlie", "age": 20, "score": 5.0},
    ]
    sorter = Sorter(make_schema(), keys=["score"])
    result = sorter.sort(records)
    assert result[-1]["score"] is None


def test_no_keys_raises():
    with pytest.raises(SortError, match="At least one sort key"):
        Sorter(make_schema(), keys=[])


def test_invalid_key_raises():
    with pytest.raises(SortError, match="not found in schema"):
        Sorter(make_schema(), keys=["nonexistent"])


def test_ascending_length_mismatch_raises():
    with pytest.raises(SortError, match="Length of 'ascending'"):
        Sorter(make_schema(), keys=["age", "score"], ascending=[True])


def test_repr():
    sorter = Sorter(make_schema(), keys=["age", "score"], ascending=[True, False])
    assert repr(sorter) == "Sorter(keys=[age ASC, score DESC])"

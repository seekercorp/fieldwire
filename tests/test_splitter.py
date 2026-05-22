import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.splitter import Splitter, SplitError


def make_schema():
    return Schema(fields=[
        FieldSchema(name="id", type=int, nullable=False),
        FieldSchema(name="value", type=float, nullable=False),
        FieldSchema(name="label", type=str, nullable=True),
    ])


RECORDS = [
    {"id": 1, "value": 10.0, "label": "a"},
    {"id": 2, "value": 20.0, "label": "b"},
    {"id": 3, "value": 5.0, "label": "a"},
    {"id": 4, "value": 50.0, "label": "c"},
    {"id": 5, "value": 15.0, "label": "b"},
]


def test_split_basic_two_buckets():
    schema = make_schema()
    splitter = Splitter(
        schema=schema,
        predicates={
            "high": lambda r: r["value"] >= 20.0,
            "low": lambda r: r["value"] < 20.0,
        },
    )
    result = splitter.apply(RECORDS)
    assert len(result["high"]) == 2
    assert len(result["low"]) == 3


def test_split_first_matching_bucket_wins():
    schema = make_schema()
    splitter = Splitter(
        schema=schema,
        predicates={
            "over_ten": lambda r: r["value"] > 10.0,
            "over_five": lambda r: r["value"] > 5.0,
        },
    )
    result = splitter.apply(RECORDS)
    # value=15 and 20 and 50 go to over_ten; value=10 goes to over_five (10 > 5 but not > 10)
    assert {r["id"] for r in result["over_ten"]} == {2, 4, 5}
    assert {r["id"] for r in result["over_five"]} == {1}


def test_split_default_bucket_catches_unmatched():
    schema = make_schema()
    splitter = Splitter(
        schema=schema,
        predicates={"high": lambda r: r["value"] >= 20.0},
        default_bucket="other",
    )
    result = splitter.apply(RECORDS)
    assert len(result["high"]) == 2
    assert len(result["other"]) == 3


def test_split_no_default_unmatched_dropped():
    schema = make_schema()
    splitter = Splitter(
        schema=schema,
        predicates={"high": lambda r: r["value"] >= 100.0},
    )
    result = splitter.apply(RECORDS)
    assert result["high"] == []
    assert "other" not in result


def test_split_empty_records_returns_empty_buckets():
    schema = make_schema()
    splitter = Splitter(
        schema=schema,
        predicates={"a": lambda r: True, "b": lambda r: False},
    )
    result = splitter.apply([])
    assert result == {"a": [], "b": []}


def test_split_predicate_exception_raises_split_error():
    schema = make_schema()
    def bad_pred(r):
        raise ValueError("boom")
    splitter = Splitter(schema=schema, predicates={"bad": bad_pred})
    with pytest.raises(SplitError, match="boom"):
        splitter.apply(RECORDS)


def test_split_no_predicates_raises():
    schema = make_schema()
    with pytest.raises(SplitError, match="At least one predicate"):
        Splitter(schema=schema, predicates={})


def test_split_repr():
    schema = make_schema()
    splitter = Splitter(
        schema=schema,
        predicates={"high": lambda r: True},
        default_bucket="rest",
    )
    r = repr(splitter)
    assert "high" in r
    assert "rest" in r

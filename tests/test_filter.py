import pytest
from fieldwire.filter import Filter, FilterError
from fieldwire.schema import Schema, FieldSchema


def make_schema():
    return Schema(
        fields=[
            FieldSchema(name="id", type=int, nullable=False),
            FieldSchema(name="value", type=float, nullable=True),
            FieldSchema(name="label", type=str, nullable=False),
        ]
    )


ROWS = [
    {"id": 1, "value": 10.0, "label": "a"},
    {"id": 2, "value": 20.0, "label": "b"},
    {"id": 3, "value": 5.0, "label": "a"},
    {"id": 4, "value": None, "label": "c"},
]


def test_filter_basic_predicate():
    f = Filter(predicate=lambda row: row["value"] is not None and row["value"] > 8.0)
    result = f.apply(ROWS)
    assert len(result) == 2
    assert all(r["value"] > 8.0 for r in result)


def test_filter_by_label():
    f = Filter(predicate=lambda row: row["label"] == "a")
    result = f.apply(ROWS)
    assert len(result) == 2
    assert all(r["label"] == "a" for r in result)


def test_filter_all_pass():
    f = Filter(predicate=lambda row: True)
    result = f.apply(ROWS)
    assert result == ROWS


def test_filter_none_pass():
    f = Filter(predicate=lambda row: False)
    result = f.apply(ROWS)
    assert result == []


def test_filter_does_not_mutate_original():
    original = [{"id": 1, "value": 1.0, "label": "x"}]
    f = Filter(predicate=lambda row: row["value"] > 5.0)
    result = f.apply(original)
    assert result == []
    assert original == [{"id": 1, "value": 1.0, "label": "x"}]


def test_filter_with_valid_schema():
    schema = make_schema()
    f = Filter(predicate=lambda row: row["id"] > 2, schema=schema)
    result = f.apply(ROWS)
    assert len(result) == 2
    assert result[0]["id"] == 3


def test_filter_schema_validation_failure():
    schema = make_schema()
    bad_rows = [{"id": "not-an-int", "value": 1.0, "label": "x"}]
    f = Filter(predicate=lambda row: True, schema=schema)
    with pytest.raises(FilterError, match="schema validation"):
        f.apply(bad_rows)


def test_filter_predicate_exception_raises():
    def bad_pred(row):
        raise ValueError("oops")

    f = Filter(predicate=bad_pred)
    with pytest.raises(FilterError, match="Predicate raised an exception"):
        f.apply([{"id": 1}])


def test_filter_non_callable_raises():
    with pytest.raises(FilterError, match="predicate must be callable"):
        Filter(predicate="not a function")


def test_filter_non_list_input_raises():
    f = Filter(predicate=lambda row: True)
    with pytest.raises(FilterError, match="Expected a list"):
        f.apply({"id": 1})


def test_filter_repr():
    f = Filter(predicate=lambda row: True, name="my_filter")
    assert "my_filter" in repr(f)
    assert "Filter" in repr(f)

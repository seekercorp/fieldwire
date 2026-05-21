"""Tests for fieldwire.groupby."""

import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.aggregator import agg_sum, agg_mean, agg_count
from fieldwire.groupby import GroupBy, GroupByError


def make_schema():
    return Schema(
        fields=[
            FieldSchema(name="category", type=str, nullable=False),
            FieldSchema(name="value", type=int, nullable=False),
            FieldSchema(name="score", type=float, nullable=False),
        ]
    )


ROWS = [
    {"category": "a", "value": 1, "score": 1.0},
    {"category": "b", "value": 2, "score": 2.0},
    {"category": "a", "value": 3, "score": 3.0},
    {"category": "b", "value": 4, "score": 4.0},
    {"category": "a", "value": 5, "score": 5.0},
]


def test_groupby_sum():
    gb = GroupBy(make_schema(), "category", {"value": agg_sum})
    results = gb.run(ROWS)
    by_cat = {r["category"]: r["value"] for r in results}
    assert by_cat["a"] == 9   # 1+3+5
    assert by_cat["b"] == 6   # 2+4


def test_groupby_mean():
    gb = GroupBy(make_schema(), "category", {"score": agg_mean})
    results = gb.run(ROWS)
    by_cat = {r["category"]: r["score"] for r in results}
    assert by_cat["a"] == pytest.approx(3.0)   # (1+3+5)/3
    assert by_cat["b"] == pytest.approx(3.0)   # (2+4)/2


def test_groupby_count():
    gb = GroupBy(make_schema(), "category", {"value": agg_count})
    results = gb.run(ROWS)
    by_cat = {r["category"]: r["value"] for r in results}
    assert by_cat["a"] == 3
    assert by_cat["b"] == 2


def test_groupby_key_included_in_result():
    gb = GroupBy(make_schema(), "category", {"value": agg_sum})
    results = gb.run(ROWS)
    for r in results:
        assert "category" in r


def test_groupby_multiple_agg_fields():
    gb = GroupBy(make_schema(), "category", {"value": agg_sum, "score": agg_mean})
    results = gb.run(ROWS)
    assert len(results) == 2
    by_cat = {r["category"]: r for r in results}
    assert by_cat["a"]["value"] == 9
    assert by_cat["a"]["score"] == pytest.approx(3.0)


def test_groupby_empty_rows():
    gb = GroupBy(make_schema(), "category", {"value": agg_sum})
    results = gb.run([])
    assert results == []


def test_groupby_unknown_key_field_raises():
    with pytest.raises(GroupByError, match="not found in schema"):
        GroupBy(make_schema(), "nonexistent", {"value": agg_sum})


def test_groupby_repr():
    gb = GroupBy(make_schema(), "category", {"value": agg_sum})
    r = repr(gb)
    assert "GroupBy" in r
    assert "category" in r

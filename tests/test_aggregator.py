"""Tests for fieldwire.aggregator."""

import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.aggregator import (
    Aggregator,
    AggregationError,
    agg_sum,
    agg_mean,
    agg_count,
    agg_min,
    agg_max,
)


def make_schema():
    return Schema(
        fields=[
            FieldSchema(name="value", type=int, nullable=False),
            FieldSchema(name="score", type=float, nullable=False),
            FieldSchema(name="label", type=str, nullable=True),
        ]
    )


ROWS = [
    {"value": 1, "score": 1.5, "label": "a"},
    {"value": 2, "score": 2.5, "label": "b"},
    {"value": 3, "score": 3.0, "label": "c"},
]


def test_aggregator_sum():
    agg = Aggregator(make_schema(), {"value": agg_sum})
    result = agg.aggregate(ROWS)
    assert result == {"value": 6}


def test_aggregator_mean():
    agg = Aggregator(make_schema(), {"score": agg_mean})
    result = agg.aggregate(ROWS)
    assert result["score"] == pytest.approx(7.0 / 3)


def test_aggregator_count():
    agg = Aggregator(make_schema(), {"label": agg_count})
    result = agg.aggregate(ROWS)
    assert result == {"label": 3}


def test_aggregator_min_max():
    agg = Aggregator(make_schema(), {"value": agg_min, "score": agg_max})
    result = agg.aggregate(ROWS)
    assert result["value"] == 1
    assert result["score"] == pytest.approx(3.0)


def test_aggregator_multiple_fields():
    agg = Aggregator(make_schema(), {"value": agg_sum, "score": agg_mean})
    result = agg.aggregate(ROWS)
    assert result["value"] == 6
    assert result["score"] == pytest.approx(7.0 / 3)


def test_aggregator_empty_rows_raises():
    agg = Aggregator(make_schema(), {"value": agg_sum})
    with pytest.raises(AggregationError, match="empty"):
        agg.aggregate([])


def test_aggregator_unknown_field_raises():
    with pytest.raises(AggregationError, match="not found in schema"):
        Aggregator(make_schema(), {"nonexistent": agg_sum})


def test_aggregator_fn_exception_raises():
    def bad_fn(values):
        raise ValueError("oops")

    agg = Aggregator(make_schema(), {"value": bad_fn})
    with pytest.raises(AggregationError, match="oops"):
        agg.aggregate(ROWS)


def test_aggregator_repr():
    agg = Aggregator(make_schema(), {"value": agg_sum, "score": agg_mean})
    r = repr(agg)
    assert "Aggregator" in r
    assert "value" in r
    assert "score" in r


def test_agg_mean_empty_raises():
    with pytest.raises(AggregationError):
        agg_mean([])

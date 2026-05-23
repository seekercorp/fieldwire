import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.summarizer import Summarizer, SummaryError


def make_schema():
    return Schema(fields=[
        FieldSchema(name="id", type=int, nullable=False),
        FieldSchema(name="score", type=float, nullable=True),
        FieldSchema(name="count", type=int, nullable=True),
    ])


def make_records():
    return [
        {"id": 1, "score": 10.0, "count": 3},
        {"id": 2, "score": 20.0, "count": 7},
        {"id": 3, "score": None, "count": 2},
    ]


def test_unknown_field_raises():
    schema = make_schema()
    with pytest.raises(SummaryError, match="not found in schema"):
        Summarizer(schema=schema, specs={"nonexistent": "sum"})


def test_unknown_aggregation_raises():
    schema = make_schema()
    with pytest.raises(SummaryError, match="Unknown aggregation"):
        Summarizer(schema=schema, specs={"score": "median"})


def test_sum():
    schema = make_schema()
    s = Summarizer(schema=schema, specs={"score": "sum"})
    result = s.summarize(make_records())
    assert result["score_sum"] == 30.0


def test_mean_skips_none():
    schema = make_schema()
    s = Summarizer(schema=schema, specs={"score": "mean"})
    result = s.summarize(make_records())
    assert result["score_mean"] == pytest.approx(15.0)


def test_min_max():
    schema = make_schema()
    s = Summarizer(schema=schema, specs={"score": "min", "count": "max"})
    result = s.summarize(make_records())
    assert result["score_min"] == 10.0
    assert result["count_max"] == 7


def test_count_excludes_none():
    schema = make_schema()
    s = Summarizer(schema=schema, specs={"score": "count"})
    result = s.summarize(make_records())
    assert result["score_count"] == 2


def test_count_null():
    schema = make_schema()
    s = Summarizer(schema=schema, specs={"score": "count_null"})
    result = s.summarize(make_records())
    assert result["score_count_null"] == 1


def test_record_count_always_present():
    schema = make_schema()
    s = Summarizer(schema=schema, specs={"score": "sum"})
    result = s.summarize(make_records())
    assert result["_record_count"] == 3


def test_empty_records():
    schema = make_schema()
    s = Summarizer(schema=schema, specs={"score": "sum"})
    result = s.summarize([])
    assert result["score_sum"] == 0
    assert result["_record_count"] == 0


def test_output_field_prefix():
    schema = make_schema()
    s = Summarizer(schema=schema, specs={"score": "sum"}, output_field_prefix="agg_")
    result = s.summarize(make_records())
    assert "agg_score_sum" in result


def test_callable_spec():
    schema = make_schema()
    def my_agg(vals):
        return len(vals)
    s = Summarizer(schema=schema, specs={"score": my_agg})
    result = s.summarize(make_records())
    assert "score_my_agg" in result
    assert result["score_my_agg"] == 3


def test_multiple_specs():
    schema = make_schema()
    s = Summarizer(schema=schema, specs={"score": "sum", "count": "mean"})
    result = s.summarize(make_records())
    assert "score_sum" in result
    assert "count_mean" in result


def test_repr():
    schema = make_schema()
    s = Summarizer(schema=schema, specs={"score": "sum"}, output_field_prefix="p_")
    r = repr(s)
    assert "Summarizer" in r
    assert "prefix='p_'" in r

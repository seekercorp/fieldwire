import pytest
from fieldwire.profiler import Profiler, ProfileError
from fieldwire.schema import Schema, FieldSchema


def make_schema():
    return Schema(fields=[
        FieldSchema(name="id", dtype=int, nullable=False),
        FieldSchema(name="score", dtype=float, nullable=True),
        FieldSchema(name="label", dtype=str, nullable=True),
    ])


RECORDS = [
    {"id": 1, "score": 10.0, "label": "a"},
    {"id": 2, "score": 20.0, "label": "b"},
    {"id": 3, "score": None, "label": "a"},
    {"id": 4, "score": 40.0, "label": None},
]


def test_profile_count():
    p = Profiler()
    result = p.profile(RECORDS)
    assert result["id"].count == 4
    assert result["score"].count == 4


def test_profile_null_count():
    p = Profiler()
    result = p.profile(RECORDS)
    assert result["score"].null_count == 1
    assert result["label"].null_count == 1
    assert result["id"].null_count == 0


def test_profile_null_rate():
    p = Profiler()
    result = p.profile(RECORDS)
    assert result["score"].null_rate == pytest.approx(0.25)
    assert result["id"].null_rate == pytest.approx(0.0)


def test_profile_unique_count():
    p = Profiler()
    result = p.profile(RECORDS)
    assert result["label"].unique_count == 2  # 'a' and 'b', None excluded
    assert result["id"].unique_count == 4


def test_profile_min_max_numeric():
    p = Profiler()
    result = p.profile(RECORDS)
    assert result["score"].min == 10.0
    assert result["score"].max == 40.0


def test_profile_mean_numeric():
    p = Profiler()
    result = p.profile(RECORDS)
    assert result["score"].mean == pytest.approx((10.0 + 20.0 + 40.0) / 3)


def test_profile_mean_none_for_str():
    p = Profiler()
    result = p.profile(RECORDS)
    assert result["label"].mean is None


def test_profile_dtype_detected():
    p = Profiler()
    result = p.profile(RECORDS)
    assert result["id"].dtype == int
    assert result["score"].dtype == float
    assert result["label"].dtype == str


def test_profile_with_schema_limits_fields():
    schema = make_schema()
    p = Profiler(schema=schema)
    records = [{"id": 1, "score": 5.0, "label": "x", "extra": "ignored"}]
    result = p.profile(records)
    assert "extra" not in result
    assert "id" in result


def test_profile_empty_raises():
    p = Profiler()
    with pytest.raises(ProfileError, match="empty"):
        p.profile([])


def test_profiler_repr():
    p = Profiler()
    assert "Profiler" in repr(p)

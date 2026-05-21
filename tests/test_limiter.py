import pytest
from fieldwire.limiter import Limiter, LimitError
from fieldwire.schema import Schema, FieldSchema


def make_schema():
    return Schema(
        fields=[
            FieldSchema(name="id", type=int, nullable=False),
            FieldSchema(name="value", type=float, nullable=True),
        ]
    )


SAMPLE = [
    {"id": 1, "value": 1.0},
    {"id": 2, "value": 2.0},
    {"id": 3, "value": 3.0},
    {"id": 4, "value": 4.0},
    {"id": 5, "value": 5.0},
]


def test_limit_basic():
    limiter = Limiter(limit=3)
    result = limiter.apply(SAMPLE)
    assert len(result) == 3
    assert result[0]["id"] == 1
    assert result[2]["id"] == 3


def test_offset_basic():
    limiter = Limiter(offset=2)
    result = limiter.apply(SAMPLE)
    assert len(result) == 3
    assert result[0]["id"] == 3


def test_limit_and_offset():
    limiter = Limiter(limit=2, offset=1)
    result = limiter.apply(SAMPLE)
    assert len(result) == 2
    assert result[0]["id"] == 2
    assert result[1]["id"] == 3


def test_limit_exceeds_length():
    limiter = Limiter(limit=100)
    result = limiter.apply(SAMPLE)
    assert result == SAMPLE


def test_offset_exceeds_length():
    limiter = Limiter(offset=100)
    result = limiter.apply(SAMPLE)
    assert result == []


def test_limit_zero_returns_empty():
    limiter = Limiter(limit=0)
    result = limiter.apply(SAMPLE)
    assert result == []


def test_no_limit_no_offset_returns_all():
    limiter = Limiter()
    result = limiter.apply(SAMPLE)
    assert result == SAMPLE


def test_negative_limit_raises():
    with pytest.raises(LimitError, match="limit must be non-negative"):
        Limiter(limit=-1)


def test_negative_offset_raises():
    with pytest.raises(LimitError, match="offset must be non-negative"):
        Limiter(offset=-5)


def test_non_list_raises():
    limiter = Limiter(limit=2)
    with pytest.raises(LimitError, match="records must be a list"):
        limiter.apply({"id": 1})


def test_with_schema_stored():
    schema = make_schema()
    limiter = Limiter(limit=2, schema=schema)
    assert limiter.schema is schema
    result = limiter.apply(SAMPLE)
    assert len(result) == 2


def test_repr_with_limit_and_offset():
    limiter = Limiter(limit=5, offset=2)
    r = repr(limiter)
    assert "Limiter" in r
    assert "5" in r
    assert "2" in r


def test_does_not_mutate_original():
    limiter = Limiter(limit=2)
    original = list(SAMPLE)
    limiter.apply(original)
    assert original == SAMPLE

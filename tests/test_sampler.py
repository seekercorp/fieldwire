import pytest
from fieldwire.sampler import Sampler, SampleError


def make_records(n):
    return [{"id": i, "val": i * 2} for i in range(n)]


def test_sample_n_basic():
    records = make_records(10)
    s = Sampler(n=5, seed=42)
    result = s.apply(records)
    assert len(result) == 5


def test_sample_n_exceeds_length_returns_all():
    records = make_records(3)
    s = Sampler(n=10, seed=0)
    result = s.apply(records)
    assert len(result) == 3


def test_sample_fraction():
    records = make_records(100)
    s = Sampler(fraction=0.2, seed=7)
    result = s.apply(records)
    assert len(result) == 20


def test_sample_fraction_zero_returns_empty():
    records = make_records(10)
    s = Sampler(fraction=0.0, seed=0)
    result = s.apply(records)
    assert result == []


def test_sample_fraction_one_returns_all():
    records = make_records(10)
    s = Sampler(fraction=1.0, seed=0)
    result = s.apply(records)
    assert len(result) == 10


def test_sample_is_subset_of_original():
    records = make_records(20)
    s = Sampler(n=10, seed=99)
    result = s.apply(records)
    for r in result:
        assert r in records


def test_sample_reproducible_with_seed():
    records = make_records(50)
    r1 = Sampler(n=10, seed=1).apply(records)
    r2 = Sampler(n=10, seed=1).apply(records)
    assert r1 == r2


def test_sample_different_seeds_differ():
    records = make_records(50)
    r1 = Sampler(n=10, seed=1).apply(records)
    r2 = Sampler(n=10, seed=2).apply(records)
    assert r1 != r2


def test_sample_no_args_raises():
    with pytest.raises(SampleError, match="Either"):
        Sampler()


def test_sample_both_args_raises():
    with pytest.raises(SampleError, match="Only one"):
        Sampler(n=5, fraction=0.5)


def test_sample_negative_n_raises():
    with pytest.raises(SampleError, match="non-negative"):
        Sampler(n=-1)


def test_sample_fraction_out_of_range_raises():
    with pytest.raises(SampleError, match="between 0.0 and 1.0"):
        Sampler(fraction=1.5)


def test_sample_repr_n():
    s = Sampler(n=10, seed=42)
    assert "Sampler" in repr(s)
    assert "10" in repr(s)


def test_sample_repr_fraction():
    s = Sampler(fraction=0.3)
    assert "0.3" in repr(s)

import pytest
from fieldwire.partitioner import Partitioner, PartitionError
from fieldwire.schema import Schema, FieldSchema


def make_schema() -> Schema:
    return Schema(fields=[
        FieldSchema(name="id", type=int, nullable=False),
        FieldSchema(name="region", type=str, nullable=True),
        FieldSchema(name="value", type=float, nullable=False),
    ])


RECORDS = [
    {"id": 1, "region": "north", "value": 10.0},
    {"id": 2, "region": "south", "value": 20.0},
    {"id": 3, "region": "north", "value": 30.0},
    {"id": 4, "region": "east",  "value": 40.0},
]


def test_partition_basic():
    p = Partitioner(key_fn=lambda r: r["region"])
    result = p.apply(RECORDS)
    assert set(result.keys()) == {"north", "south", "east"}
    assert len(result["north"]) == 2
    assert len(result["south"]) == 1


def test_partition_does_not_mutate_original():
    records = [{"id": 1, "region": "north", "value": 1.0}]
    p = Partitioner(key_fn=lambda r: r["region"])
    result = p.apply(records)
    result["north"][0]["region"] = "mutated"
    assert records[0]["region"] == "north"


def test_partition_empty_records():
    p = Partitioner(key_fn=lambda r: r["region"])
    result = p.apply([])
    assert result == {}


def test_partition_default_on_key_fn_error():
    def bad_key(r):
        if r["id"] == 2:
            raise ValueError("boom")
        return r["region"]

    p = Partitioner(key_fn=bad_key, default_partition="unknown")
    result = p.apply(RECORDS)
    assert "unknown" in result
    assert any(r["id"] == 2 for r in result["unknown"])


def test_partition_key_fn_error_no_default_raises():
    def bad_key(r):
        raise RuntimeError("fail")

    p = Partitioner(key_fn=bad_key)
    with pytest.raises(PartitionError, match="key_fn raised"):
        p.apply(RECORDS)


def test_partition_none_key_with_default():
    p = Partitioner(key_fn=lambda r: None, default_partition="fallback")
    result = p.apply(RECORDS)
    assert list(result.keys()) == ["fallback"]
    assert len(result["fallback"]) == len(RECORDS)


def test_partition_none_key_no_default_raises():
    p = Partitioner(key_fn=lambda r: None)
    with pytest.raises(PartitionError, match="returned None"):
        p.apply(RECORDS)


def test_partition_names_sorted():
    p = Partitioner(key_fn=lambda r: r["region"])
    names = p.partition_names(RECORDS)
    assert names == sorted({"north", "south", "east"})


def test_non_callable_key_fn_raises():
    with pytest.raises(PartitionError, match="callable"):
        Partitioner(key_fn="not_a_function")  # type: ignore


def test_partition_repr():
    fn = lambda r: r["region"]
    fn.__name__ = "region_key"
    p = Partitioner(key_fn=fn, default_partition="other")
    assert "region_key" in repr(p)
    assert "other" in repr(p)

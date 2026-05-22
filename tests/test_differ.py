import pytest
from fieldwire.differ import Differ, DiffError, DiffResult
from fieldwire.schema import Schema, FieldSchema


def make_schema() -> Schema:
    return Schema(fields=[
        FieldSchema(name="id", type=int, nullable=False),
        FieldSchema(name="name", type=str, nullable=True),
        FieldSchema(name="score", type=float, nullable=True),
    ])


BEFORE = [
    {"id": 1, "name": "alice", "score": 10.0},
    {"id": 2, "name": "bob", "score": 20.0},
    {"id": 3, "name": "carol", "score": 30.0},
]

AFTER = [
    {"id": 1, "name": "alice", "score": 15.0},  # changed
    {"id": 2, "name": "bob", "score": 20.0},    # unchanged
    {"id": 4, "name": "dave", "score": 40.0},   # added
    # id=3 removed
]


def test_diff_added():
    d = Differ(key="id")
    result = d.diff(BEFORE, AFTER)
    assert len(result.added) == 1
    assert result.added[0]["id"] == 4


def test_diff_removed():
    d = Differ(key="id")
    result = d.diff(BEFORE, AFTER)
    assert len(result.removed) == 1
    assert result.removed[0]["id"] == 3


def test_diff_changed():
    d = Differ(key="id")
    result = d.diff(BEFORE, AFTER)
    assert len(result.changed) == 1
    entry = result.changed[0]
    assert entry["before"]["score"] == 10.0
    assert entry["after"]["score"] == 15.0


def test_diff_unchanged():
    d = Differ(key="id")
    result = d.diff(BEFORE, AFTER)
    assert len(result.unchanged) == 1
    assert result.unchanged[0]["id"] == 2


def test_has_changes_true():
    d = Differ(key="id")
    result = d.diff(BEFORE, AFTER)
    assert result.has_changes is True


def test_has_changes_false():
    d = Differ(key="id")
    result = d.diff(BEFORE, BEFORE)
    assert result.has_changes is False
    assert len(result.unchanged) == 3


def test_diff_no_changes_empty_lists():
    d = Differ(key="id")
    result = d.diff([], [])
    assert not result.has_changes
    assert result.added == []
    assert result.removed == []


def test_diff_compare_fields_limits_scope():
    before = [{"id": 1, "name": "alice", "score": 10.0}]
    after = [{"id": 1, "name": "alice_new", "score": 10.0}]
    d_all = Differ(key="id")
    d_score_only = Differ(key="id", compare_fields=["score"])
    assert len(d_all.diff(before, after).changed) == 1
    assert len(d_score_only.diff(before, after).unchanged) == 1


def test_differ_with_valid_schema():
    schema = make_schema()
    d = Differ(key="id", schema=schema)
    result = d.diff(BEFORE, AFTER)
    assert result.has_changes


def test_differ_invalid_key_raises():
    schema = make_schema()
    with pytest.raises(DiffError, match="Key field"):
        Differ(key="missing", schema=schema)


def test_differ_invalid_compare_field_raises():
    schema = make_schema()
    with pytest.raises(DiffError, match="Compare field"):
        Differ(key="id", schema=schema, compare_fields=["nonexistent"])


def test_differ_missing_key_in_record_raises():
    d = Differ(key="id")
    with pytest.raises(DiffError, match="missing key"):
        d.diff([{"name": "no_id"}], [])


def test_differ_repr():
    d = Differ(key="id", compare_fields=["score"])
    assert "id" in repr(d)
    assert "score" in repr(d)

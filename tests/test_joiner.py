import pytest
from fieldwire.joiner import Joiner, JoinError


LEFT_RECORDS = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Carol"},
]

RIGHT_RECORDS = [
    {"user_id": 1, "score": 95},
    {"user_id": 2, "score": 80},
    {"user_id": 4, "score": 70},
]


def test_inner_join_basic():
    joiner = Joiner(left_key="id", right_key="user_id", join_type="inner")
    result = joiner.join(LEFT_RECORDS, RIGHT_RECORDS)
    assert len(result) == 2
    names = {r["name"] for r in result}
    assert names == {"Alice", "Bob"}


def test_inner_join_merged_fields():
    joiner = Joiner(left_key="id", right_key="user_id", join_type="inner")
    result = joiner.join(LEFT_RECORDS, RIGHT_RECORDS)
    alice = next(r for r in result if r["name"] == "Alice")
    assert alice["score"] == 95
    assert alice["id"] == 1


def test_left_join_includes_unmatched_left():
    joiner = Joiner(left_key="id", right_key="user_id", join_type="left")
    result = joiner.join(LEFT_RECORDS, RIGHT_RECORDS)
    assert len(result) == 3
    carol = next(r for r in result if r["name"] == "Carol")
    assert carol["score"] is None


def test_right_join_includes_unmatched_right():
    joiner = Joiner(left_key="id", right_key="user_id", join_type="right")
    result = joiner.join(LEFT_RECORDS, RIGHT_RECORDS)
    assert len(result) == 3
    unmatched = next(r for r in result if r["user_id"] == 4)
    assert unmatched["name"] is None


def test_inner_join_no_matches_returns_empty():
    left = [{"id": 99, "val": "x"}]
    right = [{"ref": 1, "data": "y"}]
    joiner = Joiner(left_key="id", right_key="ref", join_type="inner")
    result = joiner.join(left, right)
    assert result == []


def test_join_empty_inputs():
    joiner = Joiner(left_key="id", right_key="id")
    result = joiner.join([], [])
    assert result == []


def test_invalid_join_type_raises():
    with pytest.raises(JoinError, match="Unsupported join type"):
        Joiner(left_key="id", right_key="id", join_type="outer")


def test_missing_left_key_raises():
    joiner = Joiner(left_key="missing", right_key="id")
    with pytest.raises(JoinError, match="Key 'missing' not found in left"):
        joiner.join([{"id": 1}], [{"id": 1}])


def test_missing_right_key_raises():
    joiner = Joiner(left_key="id", right_key="missing")
    with pytest.raises(JoinError, match="Key 'missing' not found in right"):
        joiner.join([{"id": 1}], [{"id": 1}])


def test_repr():
    joiner = Joiner(left_key="id", right_key="user_id", join_type="left")
    r = repr(joiner)
    assert "left" in r
    assert "id" in r
    assert "user_id" in r


def test_one_to_many_join():
    left = [{"id": 1, "name": "Alice"}]
    right = [
        {"user_id": 1, "tag": "admin"},
        {"user_id": 1, "tag": "editor"},
    ]
    joiner = Joiner(left_key="id", right_key="user_id", join_type="inner")
    result = joiner.join(left, right)
    assert len(result) == 2
    tags = {r["tag"] for r in result}
    assert tags == {"admin", "editor"}

import pytest
from fieldwire.scorer import Scorer, ScoreError
from fieldwire.schema import Schema, FieldSchema


def make_schema(*names: str) -> Schema:
    return Schema(fields=[FieldSchema(name=n, type=float, nullable=False) for n in names])


# --- basic scoring ---

def test_scorer_single_rule():
    scorer = Scorer(rules={"r1": lambda rec: rec["value"]})
    records = [{"value": 10.0}, {"value": 4.0}]
    result = scorer.apply(records)
    assert result[0]["score"] == pytest.approx(10.0)
    assert result[1]["score"] == pytest.approx(4.0)


def test_scorer_multiple_rules_equal_weight():
    scorer = Scorer(
        rules={
            "a": lambda rec: rec["x"],
            "b": lambda rec: rec["y"],
        }
    )
    records = [{"x": 8.0, "y": 4.0}]
    result = scorer.apply(records)
    assert result[0]["score"] == pytest.approx(6.0)


def test_scorer_weighted_rules():
    scorer = Scorer(
        rules={
            "a": lambda rec: rec["x"],
            "b": lambda rec: rec["y"],
        },
        weights={"a": 3.0, "b": 1.0},
    )
    records = [{"x": 10.0, "y": 2.0}]
    result = scorer.apply(records)
    # (10*3 + 2*1) / (3+1) = 32/4 = 8.0
    assert result[0]["score"] == pytest.approx(8.0)


def test_scorer_custom_output_field():
    scorer = Scorer(
        rules={"r": lambda rec: rec["v"]},
        output_field="rank",
    )
    records = [{"v": 5.0}]
    result = scorer.apply(records)
    assert "rank" in result[0]
    assert "score" not in result[0]


def test_scorer_does_not_mutate_original():
    scorer = Scorer(rules={"r": lambda rec: 1.0})
    original = [{"a": 1}]
    scorer.apply(original)
    assert "score" not in original[0]


def test_scorer_empty_records_returns_empty():
    scorer = Scorer(rules={"r": lambda rec: 0.0})
    assert scorer.apply([]) == []


# --- error cases ---

def test_scorer_no_rules_raises():
    with pytest.raises(ScoreError, match="At least one"):
        Scorer(rules={})


def test_scorer_missing_weight_raises():
    with pytest.raises(ScoreError, match="Weights missing"):
        Scorer(
            rules={"a": lambda r: 1.0, "b": lambda r: 2.0},
            weights={"a": 1.0},
        )


def test_scorer_output_field_in_schema_raises():
    schema = make_schema("score")
    with pytest.raises(ScoreError, match="already exists"):
        Scorer(rules={"r": lambda r: 1.0}, schema=schema)


def test_scorer_rule_exception_raises():
    def bad_rule(rec):
        raise ValueError("boom")

    scorer = Scorer(rules={"bad": bad_rule})
    with pytest.raises(ScoreError, match="bad"):
        scorer.apply([{"x": 1}])


def test_scorer_repr():
    scorer = Scorer(rules={"r1": lambda r: 1.0}, output_field="score")
    r = repr(scorer)
    assert "Scorer" in r
    assert "r1" in r

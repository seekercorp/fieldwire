import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.validator import Validator, ValidateError


def make_schema(*names_types):
    fields = [FieldSchema(name=n, dtype=t, nullable=True) for n, t in names_types]
    return Schema(fields=fields)


# ---------------------------------------------------------------------------
# Basic rule application
# ---------------------------------------------------------------------------

def test_validate_all_pass():
    records = [{"age": 25}, {"age": 30}]
    v = Validator(rules={"age": lambda x: x >= 18})
    report = v.validate(records)
    assert report["total"] == 2
    assert report["passed"] == 2
    assert report["failed"] == 0
    assert report["violations"] == []


def test_validate_some_fail():
    records = [{"age": 15}, {"age": 30}, {"age": 10}]
    v = Validator(rules={"age": lambda x: x >= 18})
    report = v.validate(records)
    assert report["failed"] == 2
    assert len(report["violations"]) == 2
    assert report["violations"][0]["index"] == 0
    assert report["violations"][1]["index"] == 2


def test_validate_violation_contains_field_and_value():
    records = [{"score": -1}]
    v = Validator(rules={"score": lambda x: x >= 0})
    report = v.validate(records)
    violation = report["violations"][0]
    assert violation["field"] == "score"
    assert violation["value"] == -1


def test_validate_multiple_rules():
    records = [
        {"age": 20, "score": 50},
        {"age": 15, "score": 110},
    ]
    v = Validator(
        rules={
            "age": lambda x: x >= 18,
            "score": lambda x: 0 <= x <= 100,
        }
    )
    report = v.validate(records)
    assert report["failed"] == 2
    fields_violated = {viol["field"] for viol in report["violations"]}
    assert "age" in fields_violated
    assert "score" in fields_violated


def test_validate_empty_records():
    v = Validator(rules={"age": lambda x: x >= 0})
    report = v.validate([])
    assert report["total"] == 0
    assert report["passed"] == 0
    assert report["failed"] == 0


def test_validate_no_rules():
    records = [{"x": 1}, {"x": 2}]
    v = Validator()
    report = v.validate(records)
    assert report["passed"] == 2
    assert report["violations"] == []


# ---------------------------------------------------------------------------
# raise_on_fail behaviour
# ---------------------------------------------------------------------------

def test_raise_on_fail_raises_validate_error():
    records = [{"val": -5}]
    v = Validator(rules={"val": lambda x: x > 0}, raise_on_fail=True)
    with pytest.raises(ValidateError, match="val"):
        v.validate(records)


def test_raise_on_fail_predicate_exception_raises():
    def bad_rule(x):
        raise RuntimeError("oops")

    records = [{"val": 1}]
    v = Validator(rules={"val": bad_rule}, raise_on_fail=True)
    with pytest.raises(ValidateError, match="raised an exception"):
        v.validate(records)


# ---------------------------------------------------------------------------
# Schema-aware construction
# ---------------------------------------------------------------------------

def test_schema_unknown_field_raises():
    schema = make_schema(("age", int))
    with pytest.raises(ValidateError, match="unknown field"):
        Validator(schema=schema, rules={"nonexistent": lambda x: True})


def test_schema_known_field_ok():
    schema = make_schema(("age", int))
    v = Validator(schema=schema, rules={"age": lambda x: x >= 0})
    report = v.validate([{"age": 5}])
    assert report["passed"] == 1

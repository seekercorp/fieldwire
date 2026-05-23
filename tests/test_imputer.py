import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.imputer import Imputer, ImputeError


def make_schema(*names_types):
    return Schema(fields=[FieldSchema(name=n, type=t) for n, t in names_types])


# ── mean ──────────────────────────────────────────────────────────────────────

def test_impute_mean_basic():
    records = [{"v": 1}, {"v": None}, {"v": 3}]
    imp = Imputer(fields=["v"], strategy="mean")
    result = imp.apply(records)
    assert result[1]["v"] == 2.0


def test_impute_mean_does_not_mutate_original():
    records = [{"v": None}]
    imp = Imputer(fields=["v"], strategy="mean")
    imp.apply(records)
    assert records[0]["v"] is None


def test_impute_mean_all_none_fills_none():
    records = [{"v": None}, {"v": None}]
    imp = Imputer(fields=["v"], strategy="mean")
    result = imp.apply(records)
    assert result[0]["v"] is None


# ── median ────────────────────────────────────────────────────────────────────

def test_impute_median_odd():
    records = [{"v": 1}, {"v": None}, {"v": 3}, {"v": 5}]
    imp = Imputer(fields=["v"], strategy="median")
    result = imp.apply(records)
    assert result[1]["v"] == 3  # sorted [1,3,5], mid index 1


def test_impute_median_even():
    records = [{"v": 1}, {"v": None}, {"v": 3}, {"v": 4}]
    imp = Imputer(fields=["v"], strategy="median")
    result = imp.apply(records)
    assert result[1]["v"] == 3.5  # (3+4)/2


# ── mode ──────────────────────────────────────────────────────────────────────

def test_impute_mode_basic():
    records = [{"v": "a"}, {"v": None}, {"v": "b"}, {"v": "a"}]
    imp = Imputer(fields=["v"], strategy="mode")
    result = imp.apply(records)
    assert result[1]["v"] == "a"


# ── constant ──────────────────────────────────────────────────────────────────

def test_impute_constant_basic():
    records = [{"v": None}, {"v": 10}]
    imp = Imputer(fields=["v"], strategy="constant", fill_values={"v": -1})
    result = imp.apply(records)
    assert result[0]["v"] == -1
    assert result[1]["v"] == 10


def test_impute_constant_missing_fill_value_raises():
    imp = Imputer(fields=["v", "w"], strategy="constant", fill_values={"v": 0})
    with pytest.raises(ImputeError, match="No fill value"):
        imp.apply([{"v": None, "w": None}])


# ── schema validation ─────────────────────────────────────────────────────────

def test_impute_schema_unknown_field_raises():
    schema = make_schema(("a", int))
    with pytest.raises(ImputeError, match="not found in schema"):
        Imputer(fields=["z"], strategy="mean", schema=schema)


# ── invalid strategy ──────────────────────────────────────────────────────────

def test_impute_invalid_strategy_raises():
    with pytest.raises(ImputeError, match="Unknown strategy"):
        Imputer(fields=["v"], strategy="magic")


def test_impute_constant_no_fill_values_raises():
    with pytest.raises(ImputeError, match="requires fill_values"):
        Imputer(fields=["v"], strategy="constant")


# ── multiple fields ───────────────────────────────────────────────────────────

def test_impute_multiple_fields():
    records = [
        {"a": 1, "b": None},
        {"a": None, "b": 4},
        {"a": 3, "b": 6},
    ]
    imp = Imputer(fields=["a", "b"], strategy="mean")
    result = imp.apply(records)
    assert result[1]["a"] == 2.0  # mean(1,3)
    assert result[0]["b"] == 5.0  # mean(4,6)


# ── repr ──────────────────────────────────────────────────────────────────────

def test_imputer_repr():
    imp = Imputer(fields=["x"], strategy="median")
    assert "Imputer" in repr(imp)
    assert "median" in repr(imp)

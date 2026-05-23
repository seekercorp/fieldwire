import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.outlier import Outlier, OutlierError


def make_schema(*names_types):
    fields = [FieldSchema(name=n, dtype=t) for n, t in names_types]
    return Schema(fields=fields)


# ---------------------------------------------------------------------------
# Construction guards
# ---------------------------------------------------------------------------

def test_empty_fields_raises():
    with pytest.raises(OutlierError, match="fields must not be empty"):
        Outlier(fields=[])


def test_unknown_strategy_raises():
    with pytest.raises(OutlierError, match="Unknown strategy"):
        Outlier(fields=["x"], strategy="median")


def test_non_positive_threshold_raises():
    with pytest.raises(OutlierError, match="threshold must be positive"):
        Outlier(fields=["x"], threshold=0)


def test_unknown_field_in_schema_raises():
    schema = make_schema(("value", float))
    with pytest.raises(OutlierError, match="not found in schema"):
        Outlier(fields=["missing"], schema=schema)


# ---------------------------------------------------------------------------
# IQR strategy
# ---------------------------------------------------------------------------

def _make_records(values):
    return [{"x": v} for v in values]


def test_iqr_removes_high_outlier():
    records = _make_records([10, 11, 12, 13, 14, 100])
    out = Outlier(fields=["x"], strategy="iqr", threshold=1.5)
    result = out.apply(records)
    xs = [r["x"] for r in result]
    assert 100 not in xs
    assert all(v in xs for v in [10, 11, 12, 13, 14])


def test_iqr_removes_low_outlier():
    records = _make_records([-100, 10, 11, 12, 13, 14])
    out = Outlier(fields=["x"], strategy="iqr", threshold=1.5)
    result = out.apply(records)
    xs = [r["x"] for r in result]
    assert -100 not in xs


def test_iqr_no_outliers_returns_all():
    records = _make_records([1, 2, 3, 4, 5])
    out = Outlier(fields=["x"], strategy="iqr", threshold=1.5)
    result = out.apply(records)
    assert len(result) == 5


# ---------------------------------------------------------------------------
# Z-score strategy
# ---------------------------------------------------------------------------

def test_zscore_removes_outlier():
    records = _make_records([10, 11, 10, 12, 11, 200])
    out = Outlier(fields=["x"], strategy="zscore", threshold=2.0)
    result = out.apply(records)
    xs = [r["x"] for r in result]
    assert 200 not in xs


def test_zscore_constant_values_no_removal():
    records = _make_records([5, 5, 5, 5])
    out = Outlier(fields=["x"], strategy="zscore", threshold=2.0)
    result = out.apply(records)
    assert len(result) == 4


# ---------------------------------------------------------------------------
# Flag mode (remove=False)
# ---------------------------------------------------------------------------

def test_flag_mode_adds_is_outlier_key():
    records = _make_records([10, 11, 12, 100])
    out = Outlier(fields=["x"], strategy="iqr", threshold=1.5)
    result = out.apply(records, remove=False)
    assert all("_is_outlier" in r for r in result)
    assert len(result) == 4


def test_flag_mode_marks_outlier_true():
    records = _make_records([10, 11, 12, 100])
    out = Outlier(fields=["x"], strategy="iqr", threshold=1.5)
    result = out.apply(records, remove=False)
    outlier_flags = [r["_is_outlier"] for r in result if r["x"] == 100]
    assert outlier_flags == [True]


def test_flag_mode_marks_non_outlier_false():
    records = _make_records([10, 11, 12, 100])
    out = Outlier(fields=["x"], strategy="iqr", threshold=1.5)
    result = out.apply(records, remove=False)
    normal_flags = [r["_is_outlier"] for r in result if r["x"] != 100]
    assert all(f is False for f in normal_flags)


# ---------------------------------------------------------------------------
# None / missing values
# ---------------------------------------------------------------------------

def test_none_values_not_flagged_as_outlier():
    records = [{"x": None}, {"x": 10}, {"x": 11}]
    out = Outlier(fields=["x"], strategy="iqr", threshold=1.5)
    result = out.apply(records, remove=False)
    none_row = next(r for r in result if r["x"] is None)
    assert none_row["_is_outlier"] is False


def test_empty_records_returns_empty():
    out = Outlier(fields=["x"])
    assert out.apply([]) == []


# ---------------------------------------------------------------------------
# Multi-field
# ---------------------------------------------------------------------------

def test_multi_field_outlier_removed_if_any_field_is_outlier():
    records = [
        {"x": 10, "y": 10},
        {"x": 11, "y": 200},  # y is outlier
        {"x": 12, "y": 11},
    ]
    out = Outlier(fields=["x", "y"], strategy="iqr", threshold=1.5)
    result = out.apply(records)
    assert len(result) == 2
    assert all(r["y"] != 200 for r in result)


# ---------------------------------------------------------------------------
# repr
# ---------------------------------------------------------------------------

def test_repr():
    out = Outlier(fields=["score"], strategy="zscore", threshold=3.0)
    r = repr(out)
    assert "zscore" in r
    assert "score" in r

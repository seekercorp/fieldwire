import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.detector import Detector, DetectError, AnomalyReport


def make_schema(*names_types):
    fields = [FieldSchema(name=n, dtype=t, nullable=True) for n, t in names_types]
    return Schema(fields=fields)


# ---------------------------------------------------------------------------
# AnomalyReport helpers
# ---------------------------------------------------------------------------

def test_anomaly_report_count_and_rate():
    report = AnomalyReport(total=10, anomalies=[{"index": 0, "record": {}, "reasons": ["x"]}])
    assert report.count == 1
    assert report.rate == pytest.approx(0.1)


def test_anomaly_report_zero_total_rate():
    report = AnomalyReport(total=0, anomalies=[])
    assert report.rate == 0.0


# ---------------------------------------------------------------------------
# Schema validation on construction
# ---------------------------------------------------------------------------

def test_unknown_null_field_raises():
    schema = make_schema(("a", int))
    with pytest.raises(DetectError, match="null_fields"):
        Detector(null_fields=["z"], schema=schema)


def test_unknown_range_field_raises():
    schema = make_schema(("a", int))
    with pytest.raises(DetectError, match="range_checks"):
        Detector(range_checks={"z": (0, 10)}, schema=schema)


def test_unknown_type_field_raises():
    schema = make_schema(("a", int))
    with pytest.raises(DetectError, match="type_checks"):
        Detector(type_checks={"z": int}, schema=schema)


# ---------------------------------------------------------------------------
# Null checks
# ---------------------------------------------------------------------------

def test_null_field_detected():
    records = [{"a": None, "b": 1}, {"a": 2, "b": 3}]
    det = Detector(null_fields=["a"])
    report = det.scan(records)
    assert report.count == 1
    assert report.anomalies[0]["index"] == 0


def test_null_field_no_anomaly_when_all_present():
    records = [{"a": 1}, {"a": 2}]
    det = Detector(null_fields=["a"])
    report = det.scan(records)
    assert report.count == 0


# ---------------------------------------------------------------------------
# Range checks
# ---------------------------------------------------------------------------

def test_range_check_out_of_range():
    records = [{"score": 5}, {"score": 150}]
    det = Detector(range_checks={"score": (0, 100)})
    report = det.scan(records)
    assert report.count == 1
    assert "out of range" in report.anomalies[0]["reasons"][0]


def test_range_check_boundary_values_are_valid():
    records = [{"score": 0}, {"score": 100}]
    det = Detector(range_checks={"score": (0, 100)})
    report = det.scan(records)
    assert report.count == 0


def test_range_check_none_value_skipped():
    records = [{"score": None}]
    det = Detector(range_checks={"score": (0, 100)})
    report = det.scan(records)
    assert report.count == 0


# ---------------------------------------------------------------------------
# Type checks
# ---------------------------------------------------------------------------

def test_type_check_wrong_type_detected():
    records = [{"val": "not_an_int"}, {"val": 42}]
    det = Detector(type_checks={"val": int})
    report = det.scan(records)
    assert report.count == 1
    assert "expected int" in report.anomalies[0]["reasons"][0]


def test_type_check_none_value_skipped():
    records = [{"val": None}]
    det = Detector(type_checks={"val": int})
    report = det.scan(records)
    assert report.count == 0


# ---------------------------------------------------------------------------
# Multiple checks combined
# ---------------------------------------------------------------------------

def test_multiple_reasons_on_same_record():
    records = [{"a": None, "score": 999}]
    det = Detector(null_fields=["a"], range_checks={"score": (0, 100)})
    report = det.scan(records)
    assert report.count == 1
    assert len(report.anomalies[0]["reasons"]) == 2


def test_empty_records_returns_empty_report():
    det = Detector(null_fields=["a"])
    report = det.scan([])
    assert report.total == 0
    assert report.count == 0


# ---------------------------------------------------------------------------
# repr
# ---------------------------------------------------------------------------

def test_repr_contains_key_info():
    det = Detector(null_fields=["x"], range_checks={"y": (0, 1)})
    r = repr(det)
    assert "null_fields" in r
    assert "range_checks" in r

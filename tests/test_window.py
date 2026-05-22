import pytest
from fieldwire.window import Window, WindowError
from fieldwire.schema import Schema, FieldSchema


def make_schema():
    return Schema(fields=[
        FieldSchema(name="id", type=int, nullable=False),
        FieldSchema(name="value", type=float, nullable=False),
    ])


def test_window_rolling_sum():
    records = [{"id": i, "value": float(i)} for i in range(5)]
    w = Window(field="value", func=sum, window_size=3, output_field="rolling_sum")
    result = w.apply(records)
    assert result[0]["rolling_sum"] == 0.0
    assert result[1]["rolling_sum"] == 1.0
    assert result[2]["rolling_sum"] == 3.0
    assert result[3]["rolling_sum"] == 6.0
    assert result[4]["rolling_sum"] == 9.0


def test_window_rolling_mean():
    records = [{"value": float(v)} for v in [2, 4, 6, 8]]
    w = Window(field="value", func=lambda vs: sum(vs) / len(vs), window_size=2, output_field="mean")
    result = w.apply(records)
    assert result[0]["mean"] == 2.0
    assert result[1]["mean"] == 3.0
    assert result[2]["mean"] == 5.0
    assert result[3]["mean"] == 7.0


def test_window_does_not_mutate_original():
    records = [{"value": 1.0}, {"value": 2.0}]
    w = Window(field="value", func=sum, window_size=2, output_field="rolling_sum")
    w.apply(records)
    assert "rolling_sum" not in records[0]


def test_window_min_periods_returns_none():
    records = [{"value": float(v)} for v in range(4)]
    w = Window(field="value", func=sum, window_size=3, output_field="out", min_periods=3)
    result = w.apply(records)
    assert result[0]["out"] is None
    assert result[1]["out"] is None
    assert result[2]["out"] == 3.0


def test_window_empty_records():
    w = Window(field="value", func=sum, window_size=2, output_field="out")
    assert w.apply([]) == []


def test_window_invalid_window_size():
    with pytest.raises(WindowError, match="window_size must be >= 1"):
        Window(field="value", func=sum, window_size=0, output_field="out")


def test_window_min_periods_exceeds_window_size():
    with pytest.raises(WindowError, match="min_periods cannot exceed window_size"):
        Window(field="value", func=sum, window_size=2, output_field="out", min_periods=5)


def test_window_schema_validates_field():
    schema = make_schema()
    with pytest.raises(WindowError, match="not found in schema"):
        Window(field="nonexistent", func=sum, window_size=2, output_field="out", schema=schema)


def test_window_schema_valid_field():
    schema = make_schema()
    w = Window(field="value", func=sum, window_size=2, output_field="rolling_sum", schema=schema)
    records = [{"id": 1, "value": 1.0}, {"id": 2, "value": 2.0}]
    result = w.apply(records)
    assert result[1]["rolling_sum"] == 3.0


def test_window_missing_field_in_record():
    w = Window(field="value", func=sum, window_size=2, output_field="out")
    with pytest.raises(WindowError, match="missing from record"):
        w.apply([{"other": 1}])


def test_window_function_exception_raises():
    def bad_fn(vs):
        raise ValueError("boom")
    w = Window(field="value", func=bad_fn, window_size=1, output_field="out")
    with pytest.raises(WindowError, match="boom"):
        w.apply([{"value": 1.0}])


def test_window_repr():
    w = Window(field="value", func=sum, window_size=3, output_field="out", min_periods=2)
    r = repr(w)
    assert "Window" in r
    assert "value" in r
    assert "out" in r

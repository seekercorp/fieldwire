import pytest
from fieldwire.roller import Roller, RollerError
from fieldwire.schema import Schema, FieldSchema


def make_records():
    return [{"x": float(i), "y": float(i * 2)} for i in range(5)]


def test_roller_single_sum_spec():
    roller = Roller(specs=[{"field": "x", "func": "sum", "window_size": 2, "output_field": "x_sum"}])
    result = roller.apply(make_records())
    assert result[0]["x_sum"] == 0.0
    assert result[1]["x_sum"] == 1.0
    assert result[2]["x_sum"] == 3.0


def test_roller_multiple_specs():
    specs = [
        {"field": "x", "func": "sum", "window_size": 2, "output_field": "x_sum"},
        {"field": "y", "func": "mean", "window_size": 2, "output_field": "y_mean"},
    ]
    roller = Roller(specs=specs)
    result = roller.apply(make_records())
    assert "x_sum" in result[0]
    assert "y_mean" in result[0]


def test_roller_builtin_min_max():
    records = [{"v": float(i)} for i in [3, 1, 4, 1, 5]]
    specs = [
        {"field": "v", "func": "min", "window_size": 3, "output_field": "v_min"},
        {"field": "v", "func": "max", "window_size": 3, "output_field": "v_max"},
    ]
    roller = Roller(specs=specs)
    result = roller.apply(records)
    assert result[2]["v_min"] == 1.0
    assert result[2]["v_max"] == 4.0


def test_roller_callable_func():
    roller = Roller(specs=[{"field": "x", "func": sum, "window_size": 2, "output_field": "out"}])
    result = roller.apply(make_records())
    assert result[1]["out"] == 1.0


def test_roller_unknown_func_raises():
    with pytest.raises(RollerError, match="Unknown built-in function"):
        Roller(specs=[{"field": "x", "func": "median", "window_size": 2, "output_field": "out"}])


def test_roller_invalid_func_type_raises():
    with pytest.raises(RollerError):
        Roller(specs=[{"field": "x", "func": 42, "window_size": 2, "output_field": "out"}])


def test_roller_empty_records():
    roller = Roller(specs=[{"field": "x", "func": "sum", "window_size": 2, "output_field": "out"}])
    assert roller.apply([]) == []


def test_roller_repr():
    roller = Roller(specs=[{"field": "x", "func": "sum", "window_size": 2, "output_field": "x_sum"}])
    assert "x_sum" in repr(roller)


def test_roller_count_builtin():
    records = [{"v": float(i)} for i in range(4)]
    roller = Roller(specs=[{"field": "v", "func": "count", "window_size": 3, "output_field": "cnt"}])
    result = roller.apply(records)
    assert result[0]["cnt"] == 1
    assert result[2]["cnt"] == 3
    assert result[3]["cnt"] == 3

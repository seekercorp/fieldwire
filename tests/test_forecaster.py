import pytest
from fieldwire.forecaster import Forecaster, ForecastError
from fieldwire.schema import Schema, FieldSchema


def make_schema(*names_types):
    fields = [FieldSchema(name=n, dtype=t, nullable=False) for n, t in names_types]
    return Schema(fields=fields)


def linear_forecast(values):
    """Naive linear extrapolation: last value + mean step."""
    if len(values) < 2:
        return [values[-1]] * 2
    step = (values[-1] - values[0]) / (len(values) - 1)
    return [values[-1] + step * (i + 1) for i in range(2)]


def constant_forecast(values):
    return [values[-1]] * 3


def make_records():
    return [
        {"t": 1, "val": 10.0},
        {"t": 2, "val": 20.0},
        {"t": 3, "val": 30.0},
    ]


def test_forecast_appends_columns():
    fc = Forecaster(value_field="val", steps=2, func=linear_forecast)
    result = fc.apply(make_records())
    assert "forecast_1" in result[0]
    assert "forecast_2" in result[0]


def test_forecast_correct_values():
    fc = Forecaster(value_field="val", steps=2, func=linear_forecast)
    result = fc.apply(make_records())
    # step = 10, so forecast_1 = 40, forecast_2 = 50
    assert result[0]["forecast_1"] == pytest.approx(40.0)
    assert result[0]["forecast_2"] == pytest.approx(50.0)


def test_forecast_does_not_mutate_original():
    records = make_records()
    fc = Forecaster(value_field="val", steps=2, func=linear_forecast)
    fc.apply(records)
    assert "forecast_1" not in records[0]


def test_forecast_custom_prefix():
    fc = Forecaster(value_field="val", steps=3, func=constant_forecast, output_prefix="pred_")
    result = fc.apply(make_records())
    assert "pred_1" in result[0]
    assert "pred_3" in result[0]


def test_forecast_empty_records_returns_empty():
    fc = Forecaster(value_field="val", steps=2, func=linear_forecast)
    assert fc.apply([]) == []


def test_forecast_steps_less_than_one_raises():
    with pytest.raises(ForecastError, match="steps must be >= 1"):
        Forecaster(value_field="val", steps=0, func=linear_forecast)


def test_forecast_null_value_raises():
    fc = Forecaster(value_field="val", steps=2, func=linear_forecast)
    records = [{"val": 1.0}, {"val": None}]
    with pytest.raises(ForecastError, match="Null value"):
        fc.apply(records)


def test_forecast_non_numeric_raises():
    fc = Forecaster(value_field="val", steps=2, func=linear_forecast)
    records = [{"val": "abc"}, {"val": 2.0}]
    with pytest.raises(ForecastError, match="Non-numeric"):
        fc.apply(records)


def test_forecast_func_wrong_length_raises():
    def bad_func(values):
        return [1.0]  # always returns 1 value

    fc = Forecaster(value_field="val", steps=2, func=bad_func)
    with pytest.raises(ForecastError, match="exactly 2 values"):
        fc.apply(make_records())


def test_forecast_func_exception_raises():
    def broken(values):
        raise RuntimeError("boom")

    fc = Forecaster(value_field="val", steps=2, func=broken)
    with pytest.raises(ForecastError, match="boom"):
        fc.apply(make_records())


def test_forecast_schema_missing_field_raises():
    schema = make_schema(("t", int), ("val", float))
    with pytest.raises(ForecastError, match="not found in schema"):
        Forecaster(value_field="missing", steps=2, func=linear_forecast, schema=schema)


def test_forecast_all_rows_get_same_forecast_values():
    fc = Forecaster(value_field="val", steps=2, func=constant_forecast)
    result = fc.apply(make_records())
    for row in result:
        assert row["forecast_1"] == row["forecast_1"]  # deterministic
    # all rows share the same forecast columns
    assert result[0]["forecast_1"] == result[1]["forecast_1"] == result[2]["forecast_1"]

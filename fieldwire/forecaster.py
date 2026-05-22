from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, Optional
from fieldwire.schema import Schema, field_names


class ForecastError(Exception):
    pass


@dataclass
class Forecaster:
    """Append future-value predictions to records using a forecasting function."""

    value_field: str
    steps: int
    func: Callable[[List[float]], List[float]]
    output_prefix: str = "forecast_"
    schema: Optional[Schema] = None

    def __post_init__(self) -> None:
        if self.steps < 1:
            raise ForecastError("steps must be >= 1")
        if self.schema is not None:
            names = field_names(self.schema)
            if self.value_field not in names:
                raise ForecastError(
                    f"value_field '{self.value_field}' not found in schema"
                )

    def apply(
        self, records: List[dict]
    ) -> List[dict]:
        """Return new records with forecast columns appended."""
        if not records:
            return []

        values: List[float] = []
        for r in records:
            v = r.get(self.value_field)
            if v is None:
                raise ForecastError(
                    f"Null value encountered in '{self.value_field}'; "
                    "cannot forecast with missing data"
                )
            try:
                values.append(float(v))
            except (TypeError, ValueError) as exc:
                raise ForecastError(
                    f"Non-numeric value '{v}' in field '{self.value_field}'"
                ) from exc

        try:
            predicted: List[float] = self.func(values)
        except Exception as exc:
            raise ForecastError(f"Forecasting function raised an error: {exc}") from exc

        if len(predicted) != self.steps:
            raise ForecastError(
                f"Forecasting function must return exactly {self.steps} values, "
                f"got {len(predicted)}"
            )

        result = [dict(r) for r in records]
        for i, pred in enumerate(predicted):
            key = f"{self.output_prefix}{i + 1}"
            for row in result:
                row[key] = pred

        return result

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Forecaster(value_field={self.value_field!r}, steps={self.steps}, "
            f"output_prefix={self.output_prefix!r})"
        )

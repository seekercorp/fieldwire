from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from fieldwire.schema import Schema, field_names


class ScoreError(Exception):
    pass


@dataclass
class Scorer:
    """Compute a numeric score for each record using one or more weighted scoring functions."""

    rules: Dict[str, Callable[[dict], float]]
    output_field: str = "score"
    weights: Optional[Dict[str, float]] = None
    schema: Optional[Schema] = None

    def __post_init__(self) -> None:
        if not self.rules:
            raise ScoreError("At least one scoring rule must be provided.")
        if self.weights is not None:
            missing = set(self.rules) - set(self.weights)
            if missing:
                raise ScoreError(
                    f"Weights missing for rules: {sorted(missing)}"
                )
        if self.schema is not None and self.output_field in field_names(self.schema):
            raise ScoreError(
                f"output_field '{self.output_field}' already exists in schema."
            )

    def _compute(self, record: dict) -> float:
        total_weight = 0.0
        weighted_sum = 0.0
        for name, fn in self.rules.items():
            try:
                value = float(fn(record))
            except Exception as exc:
                raise ScoreError(
                    f"Scoring rule '{name}' raised an error: {exc}"
                ) from exc
            w = self.weights[name] if self.weights is not None else 1.0
            weighted_sum += value * w
            total_weight += w
        return weighted_sum / total_weight if total_weight else 0.0

    def apply(self, records: List[dict]) -> List[dict]:
        result = []
        for record in records:
            row = dict(record)
            row[self.output_field] = self._compute(record)
            result.append(row)
        return result

    def __repr__(self) -> str:
        rule_names = list(self.rules.keys())
        return (
            f"Scorer(rules={rule_names}, output_field={self.output_field!r}, "
            f"weights={self.weights})"
        )

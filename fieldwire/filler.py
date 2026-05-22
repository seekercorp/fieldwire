from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from fieldwire.schema import Schema, field_names, get_field


class FillError(Exception):
    pass


@dataclass
class Filler:
    """Fill missing (None) values in records using a strategy or explicit values."""

    schema: Schema
    fill_values: Optional[Dict[str, Any]] = None
    strategy: Optional[str] = None  # 'forward', 'backward', 'mean', 'zero'

    def __post_init__(self):
        valid_strategies = {None, "forward", "backward", "mean", "zero"}
        if self.strategy not in valid_strategies:
            raise FillError(f"Unknown strategy '{self.strategy}'. Choose from {valid_strategies}.")
        if self.fill_values and self.strategy:
            raise FillError("Provide either fill_values or strategy, not both.")
        if self.fill_values:
            names = field_names(self.schema)
            for key in self.fill_values:
                if key not in names:
                    raise FillError(f"Field '{key}' not found in schema.")

    def apply(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not records:
            return []
        if self.fill_values:
            return self._fill_explicit(records)
        if self.strategy == "forward":
            return self._fill_forward(records)
        if self.strategy == "backward":
            return self._fill_backward(records)
        if self.strategy == "mean":
            return self._fill_mean(records)
        if self.strategy == "zero":
            return self._fill_zero(records)
        return [dict(r) for r in records]

    def _fill_explicit(self, records):
        result = []
        for rec in records:
            row = dict(rec)
            for key, val in self.fill_values.items():
                if row.get(key) is None:
                    row[key] = val
            result.append(row)
        return result

    def _fill_forward(self, records):
        result = []
        last_seen: Dict[str, Any] = {}
        for rec in records:
            row = dict(rec)
            for name in field_names(self.schema):
                if row.get(name) is None and name in last_seen:
                    row[name] = last_seen[name]
                elif row.get(name) is not None:
                    last_seen[name] = row[name]
            result.append(row)
        return result

    def _fill_backward(self, records):
        result = self._fill_forward(list(reversed(records)))
        return list(reversed(result))

    def _fill_mean(self, records):
        means: Dict[str, Any] = {}
        for name in field_names(self.schema):
            vals = [r[name] for r in records if r.get(name) is not None]
            if vals and all(isinstance(v, (int, float)) for v in vals):
                means[name] = sum(vals) / len(vals)
        result = []
        for rec in records:
            row = dict(rec)
            for name, mean_val in means.items():
                if row.get(name) is None:
                    row[name] = mean_val
            result.append(row)
        return result

    def _fill_zero(self, records):
        result = []
        for rec in records:
            row = dict(rec)
            for name in field_names(self.schema):
                if row.get(name) is None:
                    row[name] = 0
            result.append(row)
        return result

    def __repr__(self):
        return f"Filler(strategy={self.strategy!r}, fill_values={self.fill_values!r})"

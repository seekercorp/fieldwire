from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from fieldwire.schema import Schema


class ImputeError(Exception):
    pass


@dataclass
class Imputer:
    """Fills missing (None) values in numeric fields using a statistical strategy.

    Supported strategies:
        - 'mean'   : replace None with the mean of non-None values
        - 'median' : replace None with the median of non-None values
        - 'mode'   : replace None with the most frequent value
        - 'constant': replace None with a user-supplied constant per field
    """

    fields: List[str]
    strategy: str = "mean"
    fill_values: Dict[str, Any] = field(default_factory=dict)
    schema: Optional[Schema] = None

    def __post_init__(self) -> None:
        valid_strategies = {"mean", "median", "mode", "constant"}
        if self.strategy not in valid_strategies:
            raise ImputeError(
                f"Unknown strategy '{self.strategy}'. Choose from {sorted(valid_strategies)}."
            )
        if self.strategy == "constant" and not self.fill_values:
            raise ImputeError(
                "Strategy 'constant' requires fill_values mapping to be provided."
            )
        if self.schema is not None:
            schema_names = {f.name for f in self.schema.fields}
            for f in self.fields:
                if f not in schema_names:
                    raise ImputeError(f"Field '{f}' not found in schema.")

    def _compute_fill(self, records: List[Dict[str, Any]], field_name: str) -> Any:
        values = [r[field_name] for r in records if r.get(field_name) is not None]
        if not values:
            return None
        if self.strategy == "mean":
            return sum(values) / len(values)
        if self.strategy == "median":
            s = sorted(values)
            mid = len(s) // 2
            return s[mid] if len(s) % 2 == 1 else (s[mid - 1] + s[mid]) / 2
        if self.strategy == "mode":
            return max(set(values), key=values.count)
        return None  # unreachable for non-constant

    def apply(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        fills: Dict[str, Any] = {}
        for f in self.fields:
            if self.strategy == "constant":
                if f not in self.fill_values:
                    raise ImputeError(
                        f"No fill value provided for field '{f}' with strategy 'constant'."
                    )
                fills[f] = self.fill_values[f]
            else:
                fills[f] = self._compute_fill(records, f)

        result = []
        for record in records:
            row = dict(record)
            for f in self.fields:
                if row.get(f) is None:
                    row[f] = fills[f]
            result.append(row)
        return result

    def __repr__(self) -> str:
        return (
            f"Imputer(fields={self.fields!r}, strategy={self.strategy!r})"
        )

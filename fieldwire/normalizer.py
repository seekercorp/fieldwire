from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from fieldwire.schema import Schema, field_names, get_field


class NormalizeError(Exception):
    pass


@dataclass
class Normalizer:
    """Normalize numeric fields in records using min-max or z-score strategies."""

    schema: Schema
    fields: List[str]
    strategy: str = "minmax"  # 'minmax' or 'zscore'

    def __post_init__(self):
        if self.strategy not in ("minmax", "zscore"):
            raise NormalizeError(f"Unknown strategy '{self.strategy}'. Use 'minmax' or 'zscore'.")
        names = field_names(self.schema)
        for f in self.fields:
            if f not in names:
                raise NormalizeError(f"Field '{f}' not found in schema.")

    def apply(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not records:
            return []
        if self.strategy == "minmax":
            return self._minmax(records)
        return self._zscore(records)

    def _minmax(self, records):
        stats = {}
        for f in self.fields:
            vals = [r[f] for r in records if r.get(f) is not None]
            if not vals:
                stats[f] = (0, 1)
                continue
            mn, mx = min(vals), max(vals)
            stats[f] = (mn, mx if mx != mn else mn + 1)
        result = []
        for rec in records:
            row = dict(rec)
            for f in self.fields:
                if row.get(f) is not None:
                    mn, mx = stats[f]
                    row[f] = (row[f] - mn) / (mx - mn)
            result.append(row)
        return result

    def _zscore(self, records):
        stats = {}
        for f in self.fields:
            vals = [r[f] for r in records if r.get(f) is not None]
            if not vals:
                stats[f] = (0.0, 1.0)
                continue
            mean = sum(vals) / len(vals)
            variance = sum((v - mean) ** 2 for v in vals) / len(vals)
            std = variance ** 0.5 or 1.0
            stats[f] = (mean, std)
        result = []
        for rec in records:
            row = dict(rec)
            for f in self.fields:
                if row.get(f) is not None:
                    mean, std = stats[f]
                    row[f] = (row[f] - mean) / std
            result.append(row)
        return result

    def __repr__(self):
        return f"Normalizer(fields={self.fields!r}, strategy={self.strategy!r})"

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Callable
from fieldwire.schema import Schema, field_names


class OutlierError(Exception):
    pass


@dataclass
class Outlier:
    """Detects and optionally removes outlier records based on numeric fields.

    Supports two strategies:
      - 'iqr'   : inter-quartile range  (value < Q1 - k*IQR  or  value > Q3 + k*IQR)
      - 'zscore': standard-score        (|z| > threshold)
    """

    fields: List[str]
    strategy: str = "iqr"
    threshold: float = 1.5
    schema: Optional[Schema] = None
    _extra: dict = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.fields:
            raise OutlierError("fields must not be empty")
        if self.strategy not in ("iqr", "zscore"):
            raise OutlierError(f"Unknown strategy '{self.strategy}'; choose 'iqr' or 'zscore'")
        if self.threshold <= 0:
            raise OutlierError("threshold must be positive")
        if self.schema is not None:
            known = set(field_names(self.schema))
            for f in self.fields:
                if f not in known:
                    raise OutlierError(f"Field '{f}' not found in schema")

    # ------------------------------------------------------------------
    def apply(
        self,
        records: List[dict],
        *,
        remove: bool = True,
    ) -> List[dict]:
        """Return records with outliers removed (remove=True) or flagged.

        When remove=False each record gains an '_is_outlier' boolean key.
        """
        if not records:
            return []

        masks = [self._outlier_mask(records, f) for f in self.fields]
        is_outlier = [any(m[i] for m in masks) for i in range(len(records))]

        if remove:
            return [r for r, flag in zip(records, is_outlier) if not flag]

        result = []
        for r, flag in zip(records, is_outlier):
            row = dict(r)
            row["_is_outlier"] = flag
            result.append(row)
        return result

    # ------------------------------------------------------------------
    def _outlier_mask(self, records: List[dict], fname: str) -> List[bool]:
        values = []
        for r in records:
            v = r.get(fname)
            values.append(float(v) if v is not None else None)

        numeric = [v for v in values if v is not None]
        if not numeric:
            return [False] * len(records)

        if self.strategy == "iqr":
            return self._iqr_mask(values, numeric)
        return self._zscore_mask(values, numeric)

    def _iqr_mask(self, values, numeric):
        numeric_sorted = sorted(numeric)
        n = len(numeric_sorted)
        q1 = numeric_sorted[n // 4]
        q3 = numeric_sorted[(3 * n) // 4]
        iqr = q3 - q1
        lo = q1 - self.threshold * iqr
        hi = q3 + self.threshold * iqr
        return [False if v is None else (v < lo or v > hi) for v in values]

    def _zscore_mask(self, values, numeric):
        mean = sum(numeric) / len(numeric)
        variance = sum((v - mean) ** 2 for v in numeric) / len(numeric)
        std = variance ** 0.5
        if std == 0:
            return [False] * len(values)
        return [
            False if v is None else abs((v - mean) / std) > self.threshold
            for v in values
        ]

    def __repr__(self) -> str:
        return (
            f"Outlier(fields={self.fields!r}, strategy={self.strategy!r}, "
            f"threshold={self.threshold})"
        )

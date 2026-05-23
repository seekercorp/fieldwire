from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from fieldwire.schema import Schema, field_names


class DetectError(Exception):
    pass


@dataclass
class AnomalyReport:
    """Summary returned by Detector.scan."""

    total: int
    anomalies: List[Dict[str, Any]]

    @property
    def count(self) -> int:
        return len(self.anomalies)

    @property
    def rate(self) -> float:
        return self.count / self.total if self.total else 0.0

    def __repr__(self) -> str:
        return f"AnomalyReport(total={self.total}, anomalies={self.count}, rate={self.rate:.2%})"


@dataclass
class Detector:
    """Scans records for anomalies using simple rule-based checks.

    Supported checks (all optional, enabled by providing the kwarg):
      - null_fields   : list[str] — flag records where these fields are None
      - range_checks  : dict[str, tuple[float, float]] — flag out-of-range values
      - type_checks   : dict[str, type] — flag values that are not the expected type
    """

    null_fields: List[str] = field(default_factory=list)
    range_checks: Dict[str, tuple] = field(default_factory=dict)
    type_checks: Dict[str, type] = field(default_factory=dict)
    schema: Optional[Schema] = None

    def __post_init__(self) -> None:
        if self.schema is not None:
            known = set(field_names(self.schema))
            for f in self.null_fields:
                if f not in known:
                    raise DetectError(f"null_fields: field '{f}' not in schema")
            for f in self.range_checks:
                if f not in known:
                    raise DetectError(f"range_checks: field '{f}' not in schema")
            for f in self.type_checks:
                if f not in known:
                    raise DetectError(f"type_checks: field '{f}' not in schema")

    def scan(self, records: List[dict]) -> AnomalyReport:
        """Scan records and return an AnomalyReport."""
        anomalies: List[Dict[str, Any]] = []

        for idx, record in enumerate(records):
            reasons: List[str] = []

            for fname in self.null_fields:
                if record.get(fname) is None:
                    reasons.append(f"null '{fname}'")

            for fname, (lo, hi) in self.range_checks.items():
                val = record.get(fname)
                if val is not None and not (lo <= val <= hi):
                    reasons.append(f"'{fname}' value {val} out of range [{lo}, {hi}]")

            for fname, expected_type in self.type_checks.items():
                val = record.get(fname)
                if val is not None and not isinstance(val, expected_type):
                    reasons.append(
                        f"'{fname}' expected {expected_type.__name__}, got {type(val).__name__}"
                    )

            if reasons:
                anomalies.append({"index": idx, "record": record, "reasons": reasons})

        return AnomalyReport(total=len(records), anomalies=anomalies)

    def __repr__(self) -> str:
        return (
            f"Detector(null_fields={self.null_fields!r}, "
            f"range_checks={list(self.range_checks)!r}, "
            f"type_checks={list(self.type_checks)!r})"
        )

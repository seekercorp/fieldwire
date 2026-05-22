from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from fieldwire.schema import Schema, field_names


class ClipError(Exception):
    """Raised when clipping fails."""


@dataclass
class Clipper:
    """Clamps numeric field values to [lower, upper] bounds.

    Parameters
    ----------
    bounds:
        Mapping of field_name -> (lower, upper). Either bound may be None
        to leave that side unbounded.
    schema:
        Optional schema used to validate that clipped fields exist and are
        numeric before processing.
    """

    bounds: Dict[str, Tuple[Optional[float], Optional[float]]]
    schema: Optional[Schema] = field(default=None)

    def __post_init__(self) -> None:
        if not self.bounds:
            raise ClipError("bounds must not be empty")
        for fname, (lo, hi) in self.bounds.items():
            if lo is not None and hi is not None and lo > hi:
                raise ClipError(
                    f"Field '{fname}': lower bound {lo} exceeds upper bound {hi}"
                )
        if self.schema is not None:
            names = field_names(self.schema)
            for fname in self.bounds:
                if fname not in names:
                    raise ClipError(
                        f"Field '{fname}' not found in schema"
                    )

    def apply(
        self, records: List[Dict]
    ) -> List[Dict]:
        """Return new records with values clamped to the configured bounds."""
        result = []
        for record in records:
            row = dict(record)
            for fname, (lo, hi) in self.bounds.items():
                val = row.get(fname)
                if val is None:
                    continue
                if not isinstance(val, (int, float)):
                    raise ClipError(
                        f"Field '{fname}' has non-numeric value {val!r}"
                    )
                if lo is not None:
                    val = max(lo, val)
                if hi is not None:
                    val = min(hi, val)
                row[fname] = val
            result.append(row)
        return result

    def __repr__(self) -> str:  # pragma: no cover
        return f"Clipper(bounds={self.bounds!r})"

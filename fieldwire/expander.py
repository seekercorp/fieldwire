from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable
from fieldwire.schema import Schema, FieldSchema, field_names, get_field


class ExpandError(Exception):
    """Raised when a record expansion operation fails."""


@dataclass
class Expander:
    """Expands a list-valued field into multiple records, one per element.

    Parameters
    ----------
    field:        Name of the field containing a list to expand.
    schema:       Optional schema for validation.
    output_field: Name for the expanded scalar value (defaults to *field*).
    keep_index:   If True, add an ``_index`` field with the element position.
    """

    field: str
    schema: Optional[Schema] = None
    output_field: Optional[str] = None
    keep_index: bool = False

    def __post_init__(self) -> None:
        if self.schema is not None:
            names = field_names(self.schema)
            if self.field not in names:
                raise ExpandError(
                    f"Field {self.field!r} not found in schema. "
                    f"Available: {names}"
                )

    def apply(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return a new list with each list-valued field element as its own row."""
        out_key = self.output_field or self.field
        results: List[Dict[str, Any]] = []
        for row in records:
            if self.field not in row:
                raise ExpandError(
                    f"Field {self.field!r} missing from record: {row}"
                )
            value = row[self.field]
            if value is None:
                # Treat None as an empty list — yields no rows
                continue
            if not isinstance(value, list):
                raise ExpandError(
                    f"Expected a list for field {self.field!r}, "
                    f"got {type(value).__name__!r} in record: {row}"
                )
            for idx, element in enumerate(value):
                new_row = {k: v for k, v in row.items() if k != self.field}
                new_row[out_key] = element
                if self.keep_index:
                    new_row["_index"] = idx
                results.append(new_row)
        return results

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Expander(field={self.field!r}, output_field={self.output_field!r}, "
            f"keep_index={self.keep_index})"
        )

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from fieldwire.schema import Schema, FieldSchema, field_names


class ReshapeError(Exception):
    pass


@dataclass
class Reshaper:
    """Reorder and/or select a subset of fields from records.

    Parameters
    ----------
    fields:
        Ordered list of field names to keep in the output.
    schema:
        Optional input schema for validation.
    fill_missing:
        If True, fields listed in *fields* that are absent from a record
        are filled with ``None`` instead of raising an error.
    """

    fields: List[str]
    schema: Optional[Schema] = None
    fill_missing: bool = False

    def __post_init__(self) -> None:
        if not self.fields:
            raise ReshapeError("fields list must not be empty")
        if len(self.fields) != len(set(self.fields)):
            raise ReshapeError("fields list contains duplicate names")
        if self.schema is not None:
            known = set(field_names(self.schema))
            unknown = set(self.fields) - known
            if unknown:
                raise ReshapeError(
                    f"fields not found in schema: {sorted(unknown)}"
                )

    def output_schema(self) -> Optional[Schema]:
        """Return a new Schema containing only the selected fields in order."""
        if self.schema is None:
            return None
        lookup: Dict[str, FieldSchema] = {f.name: f for f in self.schema.fields}
        return Schema(fields=[lookup[name] for name in self.fields])

    def apply(
        self, records: List[Dict]
    ) -> List[Dict]:
        """Return records containing only *fields* in the specified order."""
        out: List[Dict] = []
        for i, record in enumerate(records):
            row: Dict = {}
            for name in self.fields:
                if name not in record:
                    if self.fill_missing:
                        row[name] = None
                    else:
                        raise ReshapeError(
                            f"record {i} is missing field '{name}'"
                        )
                else:
                    row[name] = record[name]
            out.append(row)
        return out

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Reshaper(fields={self.fields!r}, "
            f"fill_missing={self.fill_missing})"
        )

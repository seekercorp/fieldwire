from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from fieldwire.schema import Schema, field_names, get_field


class SelectError(Exception):
    pass


@dataclass
class Selector:
    """Select (project) a subset of fields from records, optionally renaming them."""

    fields: List[str]
    schema: Optional[Schema] = None
    aliases: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.fields:
            raise SelectError("fields must not be empty")
        if len(self.fields) != len(set(self.fields)):
            raise SelectError("fields must not contain duplicates")
        if self.schema is not None:
            known = set(field_names(self.schema))
            for f in self.fields:
                if f not in known:
                    raise SelectError(
                        f"field '{f}' not found in schema"
                    )
            for src in self.aliases:
                if src not in known:
                    raise SelectError(
                        f"alias source '{src}' not found in schema"
                    )

    def output_schema(self) -> Optional[Schema]:
        """Return a new Schema reflecting the selected (and aliased) fields."""
        if self.schema is None:
            return None
        selected = []
        for f in self.fields:
            fs = get_field(self.schema, f)
            name = self.aliases.get(f, f)
            from fieldwire.schema import FieldSchema
            selected.append(FieldSchema(name=name, type=fs.type, nullable=fs.nullable))
        from fieldwire.schema import Schema
        return Schema(fields=selected)

    def apply(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return records containing only the selected fields, with aliases applied."""
        result = []
        for record in records:
            row: Dict[str, Any] = {}
            for f in self.fields:
                if f not in record:
                    raise SelectError(
                        f"field '{f}' missing from record"
                    )
                out_name = self.aliases.get(f, f)
                row[out_name] = record[f]
            result.append(row)
        return result

    def __repr__(self) -> str:
        return (
            f"Selector(fields={self.fields!r}, aliases={self.aliases!r})"
        )

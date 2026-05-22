from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from fieldwire.schema import Schema


class AnnotateError(Exception):
    pass


@dataclass
class Annotator:
    """Adds computed annotation fields to each record without modifying existing fields."""

    annotations: Dict[str, Callable[[Dict[str, Any]], Any]]
    schema: Optional[Schema] = None
    overwrite: bool = False

    def __post_init__(self) -> None:
        if not self.annotations:
            raise AnnotateError("annotations mapping must not be empty")
        if self.schema is not None:
            existing = {f.name for f in self.schema.fields}
            for key in self.annotations:
                if key in existing and not self.overwrite:
                    raise AnnotateError(
                        f"annotation key '{key}' already exists in schema; "
                        "set overwrite=True to allow"
                    )

    def apply(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = []
        for i, record in enumerate(records):
            row = dict(record)
            for key, fn in self.annotations.items():
                if key in row and not self.overwrite:
                    raise AnnotateError(
                        f"field '{key}' already present in record at index {i}; "
                        "set overwrite=True to allow"
                    )
                try:
                    row[key] = fn(record)
                except Exception as exc:
                    raise AnnotateError(
                        f"annotation '{key}' failed on record at index {i}: {exc}"
                    ) from exc
            result.append(row)
        return result

    def __repr__(self) -> str:
        keys = list(self.annotations.keys())
        return f"Annotator(annotations={keys}, overwrite={self.overwrite})"

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from fieldwire.schema import Schema, FieldSchema


class EmbedError(Exception):
    """Raised when embedding fails."""


@dataclass
class Embedder:
    """Adds a new numeric-list field to each record by applying an embed_fn.

    Parameters
    ----------
    input_field:  name of the source field (must exist in schema)
    output_field: name of the new field that will hold the embedding vector
    embed_fn:     callable(value) -> list[float]
    schema:       optional Schema for input validation
    overwrite:    if True, allow overwriting an existing output_field
    """

    input_field: str
    output_field: str
    embed_fn: Callable
    schema: Optional[Schema] = None
    overwrite: bool = False

    def __post_init__(self) -> None:
        if self.schema is not None:
            names = [f.name for f in self.schema.fields]
            if self.input_field not in names:
                raise EmbedError(
                    f"input_field '{self.input_field}' not found in schema"
                )
            if not self.overwrite and self.output_field in names:
                raise EmbedError(
                    f"output_field '{self.output_field}' already exists in schema; "
                    "set overwrite=True to allow"
                )

    def output_schema(self) -> Optional[Schema]:
        """Return a new Schema with the embedding field appended (list type)."""
        if self.schema is None:
            return None
        new_fields = list(self.schema.fields) + [
            FieldSchema(name=self.output_field, type=list, nullable=False)
        ]
        return Schema(fields=new_fields)

    def apply(self, records: List[dict]) -> List[dict]:
        """Return new records with the embedding vector added."""
        out = []
        for record in records:
            if self.input_field not in record:
                raise EmbedError(
                    f"Record missing input_field '{self.input_field}'"
                )
            try:
                vector = self.embed_fn(record[self.input_field])
            except Exception as exc:
                raise EmbedError(
                    f"embed_fn raised an error for value "
                    f"{record[self.input_field]!r}: {exc}"
                ) from exc
            if not isinstance(vector, list):
                raise EmbedError(
                    f"embed_fn must return a list, got {type(vector).__name__}"
                )
            new_record = {**record, self.output_field: vector}
            out.append(new_record)
        return out

    def __repr__(self) -> str:
        return (
            f"Embedder(input_field={self.input_field!r}, "
            f"output_field={self.output_field!r})"
        )

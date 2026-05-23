from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from fieldwire.schema import Schema, field_names


class TruncateError(Exception):
    pass


@dataclass
class Truncator:
    """Truncate string fields to a maximum length, optionally appending a suffix."""

    fields: list[str]
    max_length: int
    suffix: str = ""
    schema: Optional[Schema] = None

    def __post_init__(self) -> None:
        if self.max_length < 0:
            raise TruncateError("max_length must be non-negative")
        if not self.fields:
            raise TruncateError("fields must not be empty")
        if self.schema is not None:
            known = field_names(self.schema)
            for f in self.fields:
                if f not in known:
                    raise TruncateError(f"Field '{f}' not found in schema")
            for f in self.fields:
                ftype = next(fs.type for fs in self.schema if fs.name == f)
                if ftype is not str:
                    raise TruncateError(
                        f"Field '{f}' must be of type str, got {ftype}"
                    )

    def apply(self, records: list[dict]) -> list[dict]:
        result = []
        for record in records:
            row = dict(record)
            for f in self.fields:
                val = row.get(f)
                if val is None:
                    pass
                elif not isinstance(val, str):
                    raise TruncateError(
                        f"Expected str for field '{f}', got {type(val).__name__}"
                    )
                elif len(val) > self.max_length:
                    cut = self.max_length - len(self.suffix)
                    if cut < 0:
                        cut = 0
                    row[f] = val[:cut] + self.suffix
            result.append(row)
        return result

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Truncator(fields={self.fields!r}, max_length={self.max_length}, "
            f"suffix={self.suffix!r})"
        )

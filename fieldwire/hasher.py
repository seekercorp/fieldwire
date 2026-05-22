from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import List, Optional

from fieldwire.schema import Schema, field_names


class HashError(Exception):
    pass


@dataclass
class Hasher:
    """Adds a deterministic hash column derived from one or more fields."""

    fields: List[str]
    output_field: str = "_hash"
    algorithm: str = "md5"
    schema: Optional[Schema] = None

    def __post_init__(self) -> None:
        if not self.fields:
            raise HashError("fields must not be empty")
        supported = {"md5", "sha1", "sha256"}
        if self.algorithm not in supported:
            raise HashError(
                f"Unsupported algorithm '{self.algorithm}'. Choose from {supported}."
            )
        if self.schema is not None:
            known = field_names(self.schema)
            for f in self.fields:
                if f not in known:
                    raise HashError(
                        f"Field '{f}' not found in schema. Available: {known}"
                    )

    def apply(self, records: List[dict]) -> List[dict]:
        results = []
        for record in records:
            parts = []
            for f in self.fields:
                if f not in record:
                    raise HashError(
                        f"Field '{f}' missing from record: {record}"
                    )
                parts.append(f"{f}={record[f]}")
            raw = "|".join(parts).encode("utf-8")
            digest = hashlib.new(self.algorithm, raw).hexdigest()
            results.append({**record, self.output_field: digest})
        return results

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Hasher(fields={self.fields!r}, output_field={self.output_field!r}, "
            f"algorithm={self.algorithm!r})"
        )

from dataclasses import dataclass, field
from typing import List, Optional
from fieldwire.schema import Schema, field_names


class DeduplicateError(Exception):
    pass


@dataclass
class Deduplicator:
    """Removes duplicate rows from a dataset based on one or more key fields."""

    keys: List[str]
    keep: str = "first"  # "first" or "last"

    def __post_init__(self):
        if not self.keys:
            raise DeduplicateError("At least one key field must be specified.")
        if self.keep not in ("first", "last"):
            raise DeduplicateError("'keep' must be 'first' or 'last'.")

    def apply(
        self,
        records: List[dict],
        schema: Optional[Schema] = None,
    ) -> List[dict]:
        if schema is not None:
            names = field_names(schema)
            for key in self.keys:
                if key not in names:
                    raise DeduplicateError(
                        f"Key field '{key}' not found in schema."
                    )

        seen = {}
        for i, record in enumerate(records):
            try:
                composite_key = tuple(record[k] for k in self.keys)
            except KeyError as exc:
                raise DeduplicateError(
                    f"Record missing key field: {exc}"
                ) from exc

            if composite_key not in seen or self.keep == "last":
                seen[composite_key] = record

        return list(seen.values())

    def __repr__(self) -> str:
        return f"Deduplicator(keys={self.keys!r}, keep={self.keep!r})"

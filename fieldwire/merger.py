from dataclasses import dataclass, field
from typing import List, Optional
from fieldwire.schema import Schema, FieldSchema, field_names


class MergeError(Exception):
    pass


@dataclass
class Merger:
    """Merges multiple lists of records sharing the same schema into one."""

    schema: Schema
    deduplicate: bool = False
    dedup_key: Optional[str] = None

    def __post_init__(self):
        names = field_names(self.schema)
        if self.deduplicate and self.dedup_key is not None:
            if self.dedup_key not in names:
                raise MergeError(
                    f"dedup_key '{self.dedup_key}' not found in schema fields: {names}"
                )

    def apply(self, *record_lists: List[dict]) -> List[dict]:
        merged: List[dict] = []
        for records in record_lists:
            merged.extend(records)

        if not self.deduplicate:
            return merged

        seen = set()
        unique: List[dict] = []
        for record in merged:
            if self.dedup_key is not None:
                key = record.get(self.dedup_key)
            else:
                key = tuple(sorted(record.items()))
            if key not in seen:
                seen.add(key)
                unique.append(record)
        return unique

    def __repr__(self) -> str:
        return (
            f"Merger(deduplicate={self.deduplicate}, dedup_key={self.dedup_key!r})"
        )

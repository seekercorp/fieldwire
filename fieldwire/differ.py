from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from fieldwire.schema import Schema, field_names


class DiffError(Exception):
    pass


@dataclass
class DiffResult:
    added: List[Dict[str, Any]]
    removed: List[Dict[str, Any]]
    changed: List[Dict[str, Any]]
    unchanged: List[Dict[str, Any]]

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


@dataclass
class Differ:
    key: str
    schema: Optional[Schema] = None
    compare_fields: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.schema is not None:
            names = field_names(self.schema)
            if self.key not in names:
                raise DiffError(f"Key field '{self.key}' not found in schema.")
            if self.compare_fields is not None:
                for f in self.compare_fields:
                    if f not in names:
                        raise DiffError(f"Compare field '{f}' not found in schema.")

    def diff(
        self,
        before: List[Dict[str, Any]],
        after: List[Dict[str, Any]],
    ) -> DiffResult:
        before_map: Dict[Any, Dict[str, Any]] = {}
        for record in before:
            k = record.get(self.key)
            if k is None:
                raise DiffError(f"Record missing key '{self.key}': {record}")
            before_map[k] = record

        after_map: Dict[Any, Dict[str, Any]] = {}
        for record in after:
            k = record.get(self.key)
            if k is None:
                raise DiffError(f"Record missing key '{self.key}': {record}")
            after_map[k] = record

        added = [after_map[k] for k in after_map if k not in before_map]
        removed = [before_map[k] for k in before_map if k not in after_map]
        changed: List[Dict[str, Any]] = []
        unchanged: List[Dict[str, Any]] = []

        for k in before_map:
            if k not in after_map:
                continue
            b_rec = before_map[k]
            a_rec = after_map[k]
            fields_to_check = self.compare_fields or [
                f for f in a_rec if f != self.key
            ]
            if any(b_rec.get(f) != a_rec.get(f) for f in fields_to_check):
                changed.append({"before": b_rec, "after": a_rec})
            else:
                unchanged.append(a_rec)

        return DiffResult(
            added=added,
            removed=removed,
            changed=changed,
            unchanged=unchanged,
        )

    def __repr__(self) -> str:
        return (
            f"Differ(key={self.key!r}, "
            f"compare_fields={self.compare_fields!r})"
        )

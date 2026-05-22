from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from fieldwire.differ import Differ, DiffResult


class ChangelogError(Exception):
    pass


@dataclass
class ChangelogEntry:
    version: int
    added: List[Dict[str, Any]]
    removed: List[Dict[str, Any]]
    changed: List[Dict[str, Any]]

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed) + len(self.changed)


@dataclass
class Changelog:
    """Tracks successive diffs between snapshots of a record list."""

    key: str
    compare_fields: Optional[List[str]] = None
    _entries: List[ChangelogEntry] = field(default_factory=list, init=False, repr=False)
    _snapshots: List[List[Dict[str, Any]]] = field(default_factory=list, init=False, repr=False)

    def commit(self, records: List[Dict[str, Any]]) -> ChangelogEntry:
        """Commit a new snapshot and record the diff against the previous one."""
        differ = Differ(key=self.key, compare_fields=self.compare_fields)
        before = self._snapshots[-1] if self._snapshots else []
        self._snapshots.append(list(records))
        result: DiffResult = differ.diff(before, records)
        entry = ChangelogEntry(
            version=len(self._entries) + 1,
            added=result.added,
            removed=result.removed,
            changed=result.changed,
        )
        self._entries.append(entry)
        return entry

    def history(self) -> List[ChangelogEntry]:
        return list(self._entries)

    def latest(self) -> Optional[ChangelogEntry]:
        return self._entries[-1] if self._entries else None

    def summary(self) -> List[Dict[str, Any]]:
        return [
            {
                "version": e.version,
                "added": len(e.added),
                "removed": len(e.removed),
                "changed": len(e.changed),
                "total_changes": e.total_changes,
            }
            for e in self._entries
        ]

    def __repr__(self) -> str:
        return (
            f"Changelog(key={self.key!r}, versions={len(self._entries)})"
        )

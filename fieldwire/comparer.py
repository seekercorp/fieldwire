from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from fieldwire.schema import Schema


class CompareError(Exception):
    pass


@dataclass
class CompareResult:
    field: str
    left_value: Any
    right_value: Any
    match: bool

    def __repr__(self) -> str:
        return (
            f"CompareResult(field={self.field!r}, "
            f"left={self.left_value!r}, right={self.right_value!r}, "
            f"match={self.match})"
        )


@dataclass
class Comparer:
    """Compare two records field-by-field and report matches/mismatches."""

    schema: Schema
    fields: Optional[List[str]] = None
    key: Optional[str] = None

    def __post_init__(self) -> None:
        schema_fields = {f.name for f in self.schema.fields}
        compare_fields = self.fields if self.fields is not None else list(schema_fields)
        if not compare_fields:
            raise CompareError("fields list must not be empty")
        unknown = set(compare_fields) - schema_fields
        if unknown:
            raise CompareError(f"Unknown fields: {sorted(unknown)}")
        if self.key is not None and self.key not in schema_fields:
            raise CompareError(f"Key field {self.key!r} not found in schema")
        self._compare_fields = compare_fields

    def compare(
        self,
        left: List[Dict[str, Any]],
        right: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Compare two lists of records, returning per-row comparison results."""
        if self.key is not None:
            return self._compare_by_key(left, right)
        return self._compare_positional(left, right)

    def _compare_positional(
        self,
        left: List[Dict[str, Any]],
        right: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        results = []
        for i, (l_rec, r_rec) in enumerate(zip(left, right)):
            row_results = []
            for f in self._compare_fields:
                lv = l_rec.get(f)
                rv = r_rec.get(f)
                row_results.append(CompareResult(field=f, left_value=lv, right_value=rv, match=lv == rv))
            results.append({"_index": i, "comparisons": row_results, "all_match": all(r.match for r in row_results)})
        return results

    def _compare_by_key(
        self,
        left: List[Dict[str, Any]],
        right: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        right_index = {r[self.key]: r for r in right}
        results = []
        for l_rec in left:
            key_val = l_rec.get(self.key)
            r_rec = right_index.get(key_val, {})
            row_results = []
            for f in self._compare_fields:
                lv = l_rec.get(f)
                rv = r_rec.get(f)
                row_results.append(CompareResult(field=f, left_value=lv, right_value=rv, match=lv == rv))
            results.append({"_key": key_val, "comparisons": row_results, "all_match": all(r.match for r in row_results)})
        return results

    def __repr__(self) -> str:
        return f"Comparer(fields={self._compare_fields!r}, key={self.key!r})"

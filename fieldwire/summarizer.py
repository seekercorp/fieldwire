from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from fieldwire.schema import Schema


class SummaryError(Exception):
    pass


_BUILTIN_AGGS: Dict[str, Callable[[List[Any]], Any]] = {
    "sum": lambda vals: sum(v for v in vals if v is not None),
    "mean": lambda vals: (
        sum(v for v in vals if v is not None) / len([v for v in vals if v is not None])
        if any(v is not None for v in vals) else None
    ),
    "min": lambda vals: min((v for v in vals if v is not None), default=None),
    "max": lambda vals: max((v for v in vals if v is not None), default=None),
    "count": lambda vals: len([v for v in vals if v is not None]),
    "count_null": lambda vals: len([v for v in vals if v is None]),
}


@dataclass
class Summarizer:
    """Produce a single summary record from a list of records."""

    schema: Schema
    specs: Dict[str, str | Callable[[List[Any]], Any]]
    output_field_prefix: str = ""

    def __post_init__(self) -> None:
        schema_fields = {f.name for f in self.schema.fields}
        for src_field, agg in self.specs.items():
            if src_field not in schema_fields:
                raise SummaryError(f"Field {src_field!r} not found in schema")
            if isinstance(agg, str) and agg not in _BUILTIN_AGGS:
                raise SummaryError(
                    f"Unknown aggregation {agg!r}. "
                    f"Choose from: {sorted(_BUILTIN_AGGS)}"
                )

    def summarize(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Return a single dict summarizing the records."""
        result: Dict[str, Any] = {}
        for src_field, agg in self.specs.items():
            values = [r.get(src_field) for r in records]
            fn = _BUILTIN_AGGS[agg] if isinstance(agg, str) else agg
            out_key = f"{self.output_field_prefix}{src_field}_{agg if isinstance(agg, str) else agg.__name__}"
            try:
                result[out_key] = fn(values)
            except Exception as exc:
                raise SummaryError(f"Aggregation failed for field {src_field!r}: {exc}") from exc
        result["_record_count"] = len(records)
        return result

    def __repr__(self) -> str:
        return f"Summarizer(specs={list(self.specs.keys())!r}, prefix={self.output_field_prefix!r})"

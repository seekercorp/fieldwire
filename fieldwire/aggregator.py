"""Aggregation utilities for fieldwire pipelines."""

from typing import Any, Callable, Dict, List, Optional
from fieldwire.schema import Schema, field_names


class AggregationError(Exception):
    """Raised when an aggregation operation fails."""


class Aggregator:
    """Aggregates rows of data using named aggregation functions.

    Each field can have one aggregation function (e.g. sum, mean, count).
    Fields without an explicit aggregator are dropped from the result.
    """

    def __init__(self, schema: Schema, agg_fns: Dict[str, Callable[[List[Any]], Any]]):
        known = set(field_names(schema))
        for key in agg_fns:
            if key not in known:
                raise AggregationError(
                    f"Aggregation key '{key}' not found in schema fields: {sorted(known)}"
                )
        self._schema = schema
        self._agg_fns = agg_fns

    def aggregate(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply aggregation functions across all rows.

        Returns a single dict with one value per aggregated field.
        """
        if not rows:
            raise AggregationError("Cannot aggregate an empty list of rows.")

        result: Dict[str, Any] = {}
        for field, fn in self._agg_fns.items():
            values = [row[field] for row in rows if field in row]
            try:
                result[field] = fn(values)
            except Exception as exc:
                raise AggregationError(
                    f"Aggregation function for field '{field}' raised an error: {exc}"
                ) from exc
        return result

    def __repr__(self) -> str:
        keys = list(self._agg_fns.keys())
        return f"Aggregator(fields={keys})"


# ---------------------------------------------------------------------------
# Built-in aggregation helpers
# ---------------------------------------------------------------------------

def agg_sum(values: List[Any]) -> Any:
    return sum(values)


def agg_mean(values: List[Any]) -> float:
    if not values:
        raise AggregationError("Cannot compute mean of empty list.")
    return sum(values) / len(values)


def agg_count(values: List[Any]) -> int:
    return len(values)


def agg_min(values: List[Any]) -> Any:
    return min(values)


def agg_max(values: List[Any]) -> Any:
    return max(values)

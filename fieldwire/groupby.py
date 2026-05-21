"""GroupBy utility for fieldwire — groups rows by a key field and aggregates."""

from typing import Any, Callable, Dict, List
from fieldwire.schema import Schema, get_field
from fieldwire.aggregator import Aggregator, AggregationError


class GroupByError(Exception):
    """Raised when a group-by operation fails."""


class GroupBy:
    """Groups rows by a key field and applies an Aggregator to each group.

    Parameters
    ----------
    schema:
        The schema describing the input rows.
    key_field:
        Name of the field to group by.
    agg_fns:
        Mapping of field name -> aggregation callable (passed to Aggregator).
    """

    def __init__(
        self,
        schema: Schema,
        key_field: str,
        agg_fns: Dict[str, Callable[[List[Any]], Any]],
    ):
        field = get_field(schema, key_field)
        if field is None:
            raise GroupByError(
                f"Key field '{key_field}' not found in schema."
            )
        self._schema = schema
        self._key_field = key_field
        self._aggregator = Aggregator(schema, agg_fns)

    def run(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group rows by key field and aggregate each group.

        Returns a list of result dicts, one per unique key value.
        Each result includes the key field value plus aggregated fields.
        """
        groups: Dict[Any, List[Dict[str, Any]]] = {}
        for row in rows:
            key_val = row.get(self._key_field)
            groups.setdefault(key_val, []).append(row)

        results = []
        for key_val, group_rows in groups.items():
            try:
                agg_result = self._aggregator.aggregate(group_rows)
            except AggregationError as exc:
                raise GroupByError(
                    f"Aggregation failed for group '{self._key_field}={key_val}': {exc}"
                ) from exc
            agg_result[self._key_field] = key_val
            results.append(agg_result)

        return results

    def __repr__(self) -> str:
        return f"GroupBy(key='{self._key_field}', aggregator={self._aggregator})"

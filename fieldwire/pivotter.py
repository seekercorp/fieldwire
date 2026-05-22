from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from fieldwire.schema import Schema, FieldSchema, field_names


class PivotError(Exception):
    pass


@dataclass
class Pivotter:
    """Pivot records by spreading unique values of a column into new fields."""

    index_field: str
    pivot_field: str
    value_field: str
    agg_fn: Callable[[List[Any]], Any] = field(default=sum)
    fill_value: Any = None

    def __post_init__(self):
        if self.index_field == self.pivot_field:
            raise PivotError("index_field and pivot_field must be different")
        if self.value_field == self.pivot_field:
            raise PivotError("value_field and pivot_field must be different")

    def _validate_schema(self, schema: Schema) -> None:
        names = field_names(schema)
        for f in (self.index_field, self.pivot_field, self.value_field):
            if f not in names:
                raise PivotError(f"Field '{f}' not found in schema")

    def apply(
        self, records: List[Dict[str, Any]], schema: Optional[Schema] = None
    ) -> List[Dict[str, Any]]:
        if schema is not None:
            self._validate_schema(schema)

        if not records:
            return []

        # Collect unique pivot values (preserve order)
        pivot_values: List[Any] = []
        seen = set()
        for r in records:
            pv = r.get(self.pivot_field)
            if pv not in seen:
                seen.add(pv)
                pivot_values.append(pv)

        # Group: index_value -> pivot_value -> list of values
        groups: Dict[Any, Dict[Any, List[Any]]] = {}
        for r in records:
            idx = r.get(self.index_field)
            pv = r.get(self.pivot_field)
            val = r.get(self.value_field)
            groups.setdefault(idx, {}).setdefault(pv, []).append(val)

        result = []
        for idx_val, pv_map in groups.items():
            row: Dict[str, Any] = {self.index_field: idx_val}
            for pv in pivot_values:
                col_name = f"{self.pivot_field}_{pv}"
                vals = pv_map.get(pv, [])
                row[col_name] = self.agg_fn(vals) if vals else self.fill_value
            result.append(row)

        return result

    def output_schema(
        self, records: List[Dict[str, Any]], schema: Optional[Schema] = None
    ) -> Schema:
        if schema is not None:
            self._validate_schema(schema)

        pivot_values: List[Any] = []
        seen = set()
        for r in records:
            pv = r.get(self.pivot_field)
            if pv not in seen:
                seen.add(pv)
                pivot_values.append(pv)

        fields = [FieldSchema(name=self.index_field, type=object, nullable=True)]
        for pv in pivot_values:
            col_name = f"{self.pivot_field}_{pv}"
            fields.append(FieldSchema(name=col_name, type=object, nullable=True))
        return Schema(fields=fields)

    def __repr__(self) -> str:
        return (
            f"Pivotter(index={self.index_field!r}, pivot={self.pivot_field!r}, "
            f"value={self.value_field!r})"
        )

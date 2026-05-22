from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from fieldwire.schema import Schema, FieldSchema, field_names


class UnpivotError(Exception):
    pass


@dataclass
class Unpivotter:
    """Melt wide-format records into long format (inverse of pivot)."""

    id_fields: List[str]
    value_fields: List[str]
    var_name: str = "variable"
    value_name: str = "value"

    def __post_init__(self):
        if not self.id_fields:
            raise UnpivotError("id_fields must not be empty")
        if not self.value_fields:
            raise UnpivotError("value_fields must not be empty")
        overlap = set(self.id_fields) & set(self.value_fields)
        if overlap:
            raise UnpivotError(f"Fields appear in both id and value lists: {overlap}")

    def _validate_schema(self, schema: Schema) -> None:
        names = set(field_names(schema))
        for f in self.id_fields + self.value_fields:
            if f not in names:
                raise UnpivotError(f"Field '{f}' not found in schema")

    def apply(
        self, records: List[Dict[str, Any]], schema: Optional[Schema] = None
    ) -> List[Dict[str, Any]]:
        if schema is not None:
            self._validate_schema(schema)

        result = []
        for record in records:
            id_part = {k: record.get(k) for k in self.id_fields}
            for vf in self.value_fields:
                row = dict(id_part)
                row[self.var_name] = vf
                row[self.value_name] = record.get(vf)
                result.append(row)
        return result

    def output_schema(self, input_schema: Optional[Schema] = None) -> Schema:
        id_type = object
        val_type = object
        if input_schema is not None:
            id_fs = [
                f for f in input_schema.fields if f.name in self.id_fields
            ]
            val_fs = [
                f for f in input_schema.fields if f.name in self.value_fields
            ]
            id_type = id_fs[0].type if len(id_fs) == 1 else object
            val_types = {f.type for f in val_fs}
            val_type = val_types.pop() if len(val_types) == 1 else object

        fields = []
        for f in (self.id_fields):
            fields.append(FieldSchema(name=f, type=id_type, nullable=True))
        fields.append(FieldSchema(name=self.var_name, type=str, nullable=False))
        fields.append(FieldSchema(name=self.value_name, type=val_type, nullable=True))
        return Schema(fields=fields)

    def __repr__(self) -> str:
        return (
            f"Unpivotter(id_fields={self.id_fields!r}, "
            f"value_fields={self.value_fields!r}, "
            f"var_name={self.var_name!r}, value_name={self.value_name!r})"
        )

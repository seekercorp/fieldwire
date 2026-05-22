from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from fieldwire.schema import Schema, FieldSchema, field_names


class FlattenError(Exception):
    pass


@dataclass
class Flattener:
    """Flatten a nested dict field into top-level fields with an optional prefix."""

    schema: Schema
    field: str
    prefix: Optional[str] = None  # if None, uses field name as prefix
    separator: str = "_"

    def __post_init__(self) -> None:
        if self.field not in field_names(self.schema):
            raise FlattenError(f"Field '{self.field}' not found in schema.")
        fs = next(f for f in self.schema.fields if f.name == self.field)
        if fs.dtype is not dict:
            raise FlattenError(
                f"Field '{self.field}' must have dtype=dict to be flattened, "
                f"got {fs.dtype}."
            )

    def _effective_prefix(self) -> str:
        return self.prefix if self.prefix is not None else self.field

    def output_schema(self, sample: Dict[str, Any]) -> Schema:
        """Infer the output schema from a sample record."""
        nested = sample.get(self.field) or {}
        prefix = self._effective_prefix()
        new_fields = [f for f in self.schema.fields if f.name != self.field]
        for k, v in nested.items():
            dtype = type(v) if v is not None else str
            new_fields.append(
                FieldSchema(name=f"{prefix}{self.separator}{k}", dtype=dtype, nullable=True)
            )
        return Schema(fields=new_fields)

    def apply(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prefix = self._effective_prefix()
        result = []
        for i, record in enumerate(records):
            nested = record.get(self.field)
            if nested is not None and not isinstance(nested, dict):
                raise FlattenError(
                    f"Expected dict for field '{self.field}' at record {i}, "
                    f"got {type(nested).__name__}."
                )
            new_record = {k: v for k, v in record.items() if k != self.field}
            if nested:
                for k, v in nested.items():
                    new_record[f"{prefix}{self.separator}{k}"] = v
            result.append(new_record)
        return result

    def __repr__(self) -> str:
        return (
            f"Flattener(field='{self.field}', prefix='{self._effective_prefix()}', "
            f"separator='{self.separator}')"
        )

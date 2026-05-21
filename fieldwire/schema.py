"""Schema inference and validation for fieldwire pipelines."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, Union


PRIMITIVE_TYPE_MAP: Dict[type, str] = {
    int: "integer",
    float: "float",
    str: "string",
    bool: "boolean",
    type(None): "null",
}


@dataclass
class FieldSchema:
    name: str
    dtype: str
    nullable: bool = False
    description: str = ""

    def validate(self, value: Any) -> bool:
        """Return True if value matches this field's schema."""
        if value is None:
            return self.nullable
        expected = {v: k for k, v in PRIMITIVE_TYPE_MAP.items()}.get(self.dtype)
        if expected is None:
            return True  # unknown types pass through
        return isinstance(value, expected)


@dataclass
class Schema:
    fields: List[FieldSchema] = field(default_factory=list)

    def field_names(self) -> List[str]:
        return [f.name for f in self.fields]

    def get_field(self, name: str) -> Optional[FieldSchema]:
        for f in self.fields:
            if f.name == name:
                return f
        return None

    def validate_record(self, record: Dict[str, Any]) -> List[str]:
        """Validate a record against the schema. Returns a list of error messages."""
        errors: List[str] = []
        for field_schema in self.fields:
            if field_schema.name not in record:
                if not field_schema.nullable:
                    errors.append(f"Missing required field: '{field_schema.name}'")
                continue
            value = record[field_schema.name]
            if not field_schema.validate(value):
                errors.append(
                    f"Field '{field_schema.name}' expected type '{field_schema.dtype}', "
                    f"got '{type(value).__name__}'"
                )
        return errors


def infer_schema(records: List[Dict[str, Any]]) -> Schema:
    """Infer a Schema from a list of records."""
    if not records:
        return Schema()

    field_types: Dict[str, set] = {}
    field_nullable: Dict[str, bool] = {}

    for record in records:
        for key, value in record.items():
            if key not in field_types:
                field_types[key] = set()
                field_nullable[key] = False
            if value is None:
                field_nullable[key] = True
            else:
                dtype = PRIMITIVE_TYPE_MAP.get(type(value), "unknown")
                field_types[key].add(dtype)

    fields = []
    for name, types in field_types.items():
        types.discard("null")
        dtype = next(iter(types)) if len(types) == 1 else "mixed"
        fields.append(FieldSchema(name=name, dtype=dtype, nullable=field_nullable[name]))

    return Schema(fields=fields)

"""Automatic schema inference from data samples."""

from typing import Any, Dict, List, Optional
from fieldwire.schema import FieldSchema, Schema


_PYTHON_TYPE_MAP = {
    int: int,
    float: float,
    str: str,
    bool: bool,
    list: list,
    dict: dict,
}


def infer_field_schema(name: str, values: List[Any]) -> FieldSchema:
    """Infer a FieldSchema for a field given a list of observed values."""
    non_null_values = [v for v in values if v is not None]
    nullable = len(non_null_values) < len(values)

    if not non_null_values:
        # All values are None; fall back to Any (use str as default)
        return FieldSchema(name=name, dtype=str, nullable=True)

    observed_types = set(type(v) for v in non_null_values)

    # Promote int to float if both are present
    if int in observed_types and float in observed_types:
        observed_types.discard(int)

    if len(observed_types) == 1:
        dtype = observed_types.pop()
    else:
        # Mixed types — fall back to str
        dtype = str

    resolved_dtype = _PYTHON_TYPE_MAP.get(dtype, str)
    return FieldSchema(name=name, dtype=resolved_dtype, nullable=nullable)


def infer_schema(records: List[Dict[str, Any]], schema_name: str = "inferred") -> Schema:
    """Infer a Schema from a list of record dicts.

    Args:
        records: A list of dicts representing data rows.
        schema_name: Optional name for the resulting Schema.

    Returns:
        A Schema instance with inferred field types.

    Raises:
        ValueError: If records is empty.
    """
    if not records:
        raise ValueError("Cannot infer schema from an empty list of records.")

    all_keys: List[str] = []
    for record in records:
        for key in record:
            if key not in all_keys:
                all_keys.append(key)

    fields: List[FieldSchema] = []
    for key in all_keys:
        values = [record.get(key) for record in records]
        fields.append(infer_field_schema(key, values))

    return Schema(name=schema_name, fields=fields)

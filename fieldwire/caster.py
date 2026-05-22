from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from fieldwire.schema import Schema, FieldSchema, field_names


class CastError(Exception):
    pass


_CAST_FUNCTIONS: Dict[type, Callable[[Any], Any]] = {
    int: int,
    float: float,
    str: str,
    bool: bool,
}


@dataclass
class Caster:
    """Cast one or more fields to a target type, updating the schema accordingly."""

    schema: Schema
    casts: Dict[str, type]  # field_name -> target_type

    def __post_init__(self) -> None:
        known = field_names(self.schema)
        for fname in self.casts:
            if fname not in known:
                raise CastError(f"Field '{fname}' not found in schema.")
            target = self.casts[fname]
            if target not in _CAST_FUNCTIONS:
                raise CastError(
                    f"Unsupported cast target type '{target}' for field '{fname}'. "
                    f"Supported: {list(_CAST_FUNCTIONS.keys())}"
                )

    @property
    def output_schema(self) -> Schema:
        new_fields: List[FieldSchema] = []
        for fs in self.schema.fields:
            if fs.name in self.casts:
                new_fields.append(
                    FieldSchema(
                        name=fs.name,
                        dtype=self.casts[fs.name],
                        nullable=fs.nullable,
                    )
                )
            else:
                new_fields.append(fs)
        return Schema(fields=new_fields)

    def apply(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = []
        for i, record in enumerate(records):
            new_record = dict(record)
            for fname, target_type in self.casts.items():
                value = record.get(fname)
                if value is None:
                    fs = next(f for f in self.schema.fields if f.name == fname)
                    if not fs.nullable:
                        raise CastError(
                            f"Cannot cast None for non-nullable field '{fname}' at record {i}."
                        )
                    new_record[fname] = None
                else:
                    try:
                        new_record[fname] = _CAST_FUNCTIONS[target_type](value)
                    except (ValueError, TypeError) as exc:
                        raise CastError(
                            f"Failed to cast field '{fname}' value {value!r} "
                            f"to {target_type.__name__} at record {i}: {exc}"
                        ) from exc
            result.append(new_record)
        return result

    def __repr__(self) -> str:
        casts_str = ", ".join(f"{k}->{v.__name__}" for k, v in self.casts.items())
        return f"Caster(casts=[{casts_str}])"

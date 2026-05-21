"""Transform utilities for applying schema-aware field transformations in pipelines."""

from typing import Any, Callable, Dict, List, Optional
from fieldwire.schema import Schema, validate, field_names


class TransformError(Exception):
    """Raised when a transformation fails."""
    pass


class FieldTransform:
    """Represents a single field-level transformation."""

    def __init__(self, field: str, fn: Callable[[Any], Any], description: str = ""):
        self.field = field
        self.fn = fn
        self.description = description or f"transform({field})"

    def apply(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the transformation to a record, returning a new record."""
        if self.field not in record:
            raise TransformError(f"Field '{self.field}' not found in record.")
        result = dict(record)
        try:
            result[self.field] = self.fn(record[self.field])
        except Exception as exc:
            raise TransformError(
                f"Transform '{self.description}' failed on field '{self.field}': {exc}"
            ) from exc
        return result

    def __repr__(self) -> str:
        return f"FieldTransform(field={self.field!r}, description={self.description!r})"


class Transformer:
    """Applies a sequence of FieldTransforms to records, with optional schema validation."""

    def __init__(
        self,
        transforms: List[FieldTransform],
        input_schema: Optional[Schema] = None,
        output_schema: Optional[Schema] = None,
    ):
        self.transforms = transforms
        self.input_schema = input_schema
        self.output_schema = output_schema

    def run(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input, apply all transforms, and validate output."""
        if self.input_schema is not None:
            errors = validate(self.input_schema, record)
            if errors:
                raise TransformError(f"Input validation failed: {errors}")

        result = record
        for transform in self.transforms:
            result = transform.apply(result)

        if self.output_schema is not None:
            errors = validate(self.output_schema, result)
            if errors:
                raise TransformError(f"Output validation failed: {errors}")

        return result

    def run_batch(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply transforms to a list of records."""
        return [self.run(record) for record in records]

    def __repr__(self) -> str:
        return (
            f"Transformer(transforms={self.transforms}, "
            f"input_schema={self.input_schema}, output_schema={self.output_schema})"
        )

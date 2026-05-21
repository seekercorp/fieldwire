"""Pipeline module for building typed data transformation pipelines."""

from typing import Any, Callable, Dict, Iterable, List, Optional
from fieldwire.schema import Schema, validate


class PipelineError(Exception):
    """Raised when a pipeline step fails validation or transformation."""
    pass


class Step:
    """Represents a single transformation step in a pipeline."""

    def __init__(
        self,
        name: str,
        transform: Callable[[Dict[str, Any]], Dict[str, Any]],
        input_schema: Optional[Schema] = None,
        output_schema: Optional[Schema] = None,
    ):
        self.name = name
        self.transform = transform
        self.input_schema = input_schema
        self.output_schema = output_schema

    def run(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input, apply transform, validate output."""
        if self.input_schema is not None:
            errors = validate(self.input_schema, record)
            if errors:
                raise PipelineError(
                    f"Step '{self.name}' input validation failed: {errors}"
                )

        result = self.transform(record)

        if self.output_schema is not None:
            errors = validate(self.output_schema, result)
            if errors:
                raise PipelineError(
                    f"Step '{self.name}' output validation failed: {errors}"
                )

        return result


class Pipeline:
    """Chains multiple Steps to process records through a typed pipeline."""

    def __init__(self, name: str = "pipeline"):
        self.name = name
        self._steps: List[Step] = []

    def add_step(self, step: Step) -> "Pipeline":
        """Append a step and return self for chaining."""
        self._steps.append(step)
        return self

    def run_one(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Pass a single record through all steps."""
        current = record
        for step in self._steps:
            current = step.run(current)
        return current

    def run(self, records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process an iterable of records and return transformed results."""
        return [self.run_one(record) for record in records]

    @property
    def steps(self) -> List[Step]:
        return list(self._steps)

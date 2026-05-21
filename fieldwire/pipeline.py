"""Pipeline module: composable data transformation steps with optional schema validation."""

from typing import Any, Callable, Dict, List, Optional
from fieldwire.schema import Schema, validate
from fieldwire.inference import infer_schema


class PipelineError(Exception):
    """Raised when a pipeline step fails validation or execution."""


class Step:
    """A single transformation step in a pipeline."""

    def __init__(
        self,
        func: Callable[[Dict[str, Any]], Dict[str, Any]],
        input_schema: Optional[Schema] = None,
        output_schema: Optional[Schema] = None,
        infer_output: bool = False,
    ):
        self.func = func
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.infer_output = infer_output
        self._inferred_output_schema: Optional[Schema] = None

    def run(self, record: Dict[str, Any]) -> Dict[str, Any]:
        if self.input_schema is not None:
            errors = validate(self.input_schema, record)
            if errors:
                raise PipelineError(
                    f"Input validation failed for step '{self.func.__name__}': {errors}"
                )

        result = self.func(record)

        if self.output_schema is not None:
            errors = validate(self.output_schema, result)
            if errors:
                raise PipelineError(
                    f"Output validation failed for step '{self.func.__name__}': {errors}"
                )

        return result


class Pipeline:
    """A sequential pipeline of Steps applied to a list of records."""

    def __init__(self, steps: Optional[List[Step]] = None):
        self.steps: List[Step] = steps or []

    def add_step(self, step: Step) -> "Pipeline":
        """Append a step and return self for chaining."""
        self.steps.append(step)
        return self

    def run(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply all steps to each record in sequence."""
        results = []
        for record in records:
            current = record
            for step in self.steps:
                current = step.run(current)
            results.append(current)

        # Post-run: infer output schemas for steps that requested it
        for step in self.steps:
            if step.infer_output and results:
                step._inferred_output_schema = infer_schema(
                    results, schema_name=f"{step.func.__name__}_output"
                )

        return results

    def get_inferred_schemas(self) -> Dict[str, Optional[Schema]]:
        """Return inferred output schemas keyed by step function name."""
        return {
            step.func.__name__: step._inferred_output_schema
            for step in self.steps
            if step.infer_output
        }

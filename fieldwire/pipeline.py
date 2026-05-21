from typing import List, Dict, Any, Optional, Callable
from fieldwire.schema import Schema, validate


class PipelineError(Exception):
    pass


class Step:
    """A single step in a pipeline wrapping a callable transform."""

    def __init__(
        self,
        fn: Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]],
        input_schema: Optional[Schema] = None,
        output_schema: Optional[Schema] = None,
        name: Optional[str] = None,
    ):
        self.fn = fn
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.name = name or getattr(fn, "__name__", repr(fn))

    def run(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if self.input_schema is not None:
            for i, record in enumerate(records):
                errors = validate(record, self.input_schema)
                if errors:
                    raise PipelineError(
                        f"Step '{self.name}' input validation failed on record {i}: {errors}"
                    )
        result = self.fn(records)
        if self.output_schema is not None:
            for i, record in enumerate(result):
                errors = validate(record, self.output_schema)
                if errors:
                    raise PipelineError(
                        f"Step '{self.name}' output validation failed on record {i}: {errors}"
                    )
        return result

    def __repr__(self) -> str:
        return (
            f"Step(name={self.name!r}, input_schema={self.input_schema!r}, "
            f"output_schema={self.output_schema!r})"
        )


class Pipeline:
    """Chains multiple Steps, passing records through each in sequence."""

    def __init__(self, steps: Optional[List[Step]] = None):
        self.steps: List[Step] = steps or []

    def add_step(self, step: Step) -> "Pipeline":
        self.steps.append(step)
        return self

    def run(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not isinstance(records, list):
            raise PipelineError("Pipeline input must be a list of records")
        current = records
        for step in self.steps:
            try:
                current = step.run(current)
            except PipelineError:
                raise
            except Exception as exc:
                raise PipelineError(
                    f"Step '{step.name}' raised an unexpected error: {exc}"
                ) from exc
        return current

    def __repr__(self) -> str:
        step_names = [s.name for s in self.steps]
        return f"Pipeline(steps={step_names!r})"

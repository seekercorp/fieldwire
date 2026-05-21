from typing import Any, Callable, Dict, List, Optional
from fieldwire.schema import Schema, validate


class PipelineError(Exception):
    pass


class Step:
    """A single processing step in a pipeline."""

    def __init__(
        self,
        fn: Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]],
        input_schema: Optional[Schema] = None,
        output_schema: Optional[Schema] = None,
        name: Optional[str] = None,
    ):
        if not callable(fn):
            raise PipelineError("fn must be callable")
        self.fn = fn
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.name = name or fn.__name__

    def run(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if self.input_schema is not None:
            for i, row in enumerate(rows):
                errors = validate(self.input_schema, row)
                if errors:
                    raise PipelineError(
                        f"Step '{self.name}' input row {i} invalid: {'; '.join(errors)}"
                    )
        try:
            result = self.fn(rows)
        except PipelineError:
            raise
        except Exception as exc:
            raise PipelineError(
                f"Step '{self.name}' raised an exception: {exc}"
            ) from exc

        if self.output_schema is not None:
            for i, row in enumerate(result):
                errors = validate(self.output_schema, row)
                if errors:
                    raise PipelineError(
                        f"Step '{self.name}' output row {i} invalid: {'; '.join(errors)}"
                    )
        return result

    def __repr__(self) -> str:
        return f"Step(name={self.name!r})"


class Pipeline:
    """Chains multiple Steps together, passing output of one to the next."""

    def __init__(self, steps: Optional[List[Step]] = None, name: Optional[str] = None):
        self.steps: List[Step] = steps or []
        self.name = name or "pipeline"

    def add_step(self, step: Step) -> "Pipeline":
        if not isinstance(step, Step):
            raise PipelineError(f"Expected a Step instance, got {type(step).__name__}")
        self.steps.append(step)
        return self

    def run(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not isinstance(rows, list):
            raise PipelineError(f"Expected a list of rows, got {type(rows).__name__}")
        current = rows
        for step in self.steps:
            current = step.run(current)
        return current

    def __repr__(self) -> str:
        steps_repr = ", ".join(repr(s) for s in self.steps)
        return f"Pipeline(name={self.name!r}, steps=[{steps_repr}])"

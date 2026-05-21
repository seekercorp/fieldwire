from typing import Any, Callable, Dict, List, Optional
from fieldwire.schema import Schema, validate, field_names


class PipelineError(Exception):
    pass


class Step:
    def __init__(
        self,
        fn: Callable[[Dict[str, Any]], Dict[str, Any]],
        input_schema: Optional[Schema] = None,
        output_schema: Optional[Schema] = None,
        name: Optional[str] = None,
    ):
        self.fn = fn
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.name = name or fn.__name__

    def run(self, record: Dict[str, Any]) -> Dict[str, Any]:
        if self.input_schema:
            errors = validate(record, self.input_schema)
            if errors:
                raise PipelineError(
                    f"Step '{self.name}' input validation failed: {errors}"
                )
        result = self.fn(record)
        if self.output_schema:
            errors = validate(result, self.output_schema)
            if errors:
                raise PipelineError(
                    f"Step '{self.name}' output validation failed: {errors}"
                )
        return result

    def __repr__(self) -> str:
        return f"Step(name={self.name!r})"


class Pipeline:
    def __init__(self, steps: Optional[List[Step]] = None):
        self.steps: List[Step] = steps or []

    def add_step(self, step: Step) -> "Pipeline":
        self.steps.append(step)
        return self

    def run(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for record in records:
            current = record
            for step in self.steps:
                try:
                    current = step.run(current)
                except PipelineError:
                    raise
                except Exception as exc:
                    raise PipelineError(
                        f"Step '{step.name}' raised an unexpected error: {exc}"
                    ) from exc
            results.append(current)
        return results

    def run_batch(
        self,
        records: List[Dict[str, Any]],
        on_error: str = "raise",
    ) -> List[Dict[str, Any]]:
        if on_error not in ("raise", "skip"):
            raise PipelineError(
                f"Invalid on_error value '{on_error}'. Choose 'raise' or 'skip'."
            )
        results = []
        for record in records:
            try:
                results.append(self.run([record])[0])
            except PipelineError:
                if on_error == "raise":
                    raise
        return results

    def __repr__(self) -> str:
        step_names = [s.name for s in self.steps]
        return f"Pipeline(steps={step_names})"

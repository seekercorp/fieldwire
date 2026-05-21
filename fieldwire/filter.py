from typing import Any, Callable, Dict, List, Optional
from fieldwire.schema import Schema, validate


class FilterError(Exception):
    pass


class Filter:
    """Filters rows from a dataset based on a predicate function."""

    def __init__(
        self,
        predicate: Callable[[Dict[str, Any]], bool],
        schema: Optional[Schema] = None,
        name: Optional[str] = None,
    ):
        if not callable(predicate):
            raise FilterError("predicate must be callable")
        self.predicate = predicate
        self.schema = schema
        self.name = name or predicate.__name__

    def apply(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return only rows for which predicate returns True."""
        if not isinstance(rows, list):
            raise FilterError(f"Expected a list of rows, got {type(rows).__name__}")

        if self.schema is not None:
            for i, row in enumerate(rows):
                errors = validate(self.schema, row)
                if errors:
                    raise FilterError(
                        f"Row {i} failed schema validation: {'; '.join(errors)}"
                    )

        result = []
        for i, row in enumerate(rows):
            try:
                keep = self.predicate(row)
            except Exception as exc:
                raise FilterError(
                    f"Predicate raised an exception on row {i}: {exc}"
                ) from exc
            if keep:
                result.append(row)
        return result

    def __repr__(self) -> str:
        schema_info = f", schema={self.schema}" if self.schema else ""
        return f"Filter(name={self.name!r}{schema_info})"

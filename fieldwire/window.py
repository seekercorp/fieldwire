from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from fieldwire.schema import Schema, field_names


class WindowError(Exception):
    pass


@dataclass
class Window:
    """Applies a rolling or expanding window function over a numeric field."""

    field: str
    func: Callable[[List[Any]], Any]
    window_size: int
    output_field: str
    schema: Optional[Schema] = None
    min_periods: int = 1

    def __post_init__(self):
        if self.window_size < 1:
            raise WindowError("window_size must be >= 1")
        if self.min_periods < 1:
            raise WindowError("min_periods must be >= 1")
        if self.min_periods > self.window_size:
            raise WindowError("min_periods cannot exceed window_size")
        if self.schema is not None:
            names = field_names(self.schema)
            if self.field not in names:
                raise WindowError(f"Field '{self.field}' not found in schema")

    def apply(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not records:
            return []
        results = []
        for i, record in enumerate(records):
            if self.field not in record:
                raise WindowError(f"Field '{self.field}' missing from record at index {i}")
            start = max(0, i - self.window_size + 1)
            window_values = [records[j][self.field] for j in range(start, i + 1)]
            if len(window_values) < self.min_periods:
                computed = None
            else:
                try:
                    computed = self.func(window_values)
                except Exception as exc:
                    raise WindowError(f"Window function raised at index {i}: {exc}") from exc
            new_record = dict(record)
            new_record[self.output_field] = computed
            results.append(new_record)
        return results

    def __repr__(self) -> str:
        return (
            f"Window(field={self.field!r}, output_field={self.output_field!r}, "
            f"window_size={self.window_size}, min_periods={self.min_periods})"
        )

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from fieldwire.schema import Schema, field_names


class ProfileError(Exception):
    pass


@dataclass
class FieldProfile:
    name: str
    dtype: type
    count: int
    null_count: int
    unique_count: int
    min: Optional[Any] = None
    max: Optional[Any] = None
    mean: Optional[float] = None

    @property
    def null_rate(self) -> float:
        return self.null_count / self.count if self.count else 0.0


@dataclass
class Profiler:
    schema: Optional[Schema] = None

    def profile(self, records: List[Dict[str, Any]]) -> Dict[str, FieldProfile]:
        if not records:
            raise ProfileError("Cannot profile an empty record list.")

        keys = field_names(self.schema) if self.schema else list(records[0].keys())
        result: Dict[str, FieldProfile] = {}

        for key in keys:
            values = [r.get(key) for r in records]
            non_null = [v for v in values if v is not None]
            null_count = len(values) - len(non_null)
            unique_count = len(set(non_null))

            dtype = type(non_null[0]) if non_null else type(None)

            min_val: Optional[Any] = None
            max_val: Optional[Any] = None
            mean_val: Optional[float] = None

            if non_null and dtype in (int, float):
                try:
                    min_val = min(non_null)
                    max_val = max(non_null)
                    mean_val = sum(non_null) / len(non_null)
                except TypeError:
                    pass
            elif non_null:
                try:
                    min_val = min(non_null)
                    max_val = max(non_null)
                except TypeError:
                    pass

            result[key] = FieldProfile(
                name=key,
                dtype=dtype,
                count=len(values),
                null_count=null_count,
                unique_count=unique_count,
                min=min_val,
                max=max_val,
                mean=mean_val,
            )

        return result

    def __repr__(self) -> str:
        return f"Profiler(schema={self.schema!r})"

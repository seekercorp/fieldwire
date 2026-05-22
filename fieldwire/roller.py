from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from fieldwire.schema import Schema, FieldSchema, field_names
from fieldwire.window import Window, WindowError


class RollerError(Exception):
    pass


_BUILTIN_FUNCS: Dict[str, Callable[[List[Any]], Any]] = {
    "sum": sum,
    "mean": lambda vs: sum(vs) / len(vs),
    "min": min,
    "max": max,
    "count": len,
    "first": lambda vs: vs[0],
    "last": lambda vs: vs[-1],
}


@dataclass
class Roller:
    """High-level helper that creates and applies multiple Window operations."""

    specs: List[Dict[str, Any]]
    schema: Optional[Schema] = None

    def __post_init__(self):
        self._windows: List[Window] = []
        for spec in self.specs:
            func_name = spec.get("func")
            if isinstance(func_name, str):
                if func_name not in _BUILTIN_FUNCS:
                    raise RollerError(
                        f"Unknown built-in function '{func_name}'. "
                        f"Choose from: {list(_BUILTIN_FUNCS)}"
                    )
                func = _BUILTIN_FUNCS[func_name]
            elif callable(func_name):
                func = func_name
            else:
                raise RollerError("'func' must be a string name or callable")
            try:
                w = Window(
                    field=spec["field"],
                    func=func,
                    window_size=spec["window_size"],
                    output_field=spec["output_field"],
                    schema=self.schema,
                    min_periods=spec.get("min_periods", 1),
                )
            except WindowError as exc:
                raise RollerError(str(exc)) from exc
            self._windows.append(w)

    def apply(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        current = records
        for w in self._windows:
            try:
                current = w.apply(current)
            except WindowError as exc:
                raise RollerError(str(exc)) from exc
        return current

    def __repr__(self) -> str:
        names = [s["output_field"] for s in self.specs]
        return f"Roller(outputs={names})"

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple
from fieldwire.schema import Schema
from fieldwire.partitioner import Partitioner, PartitionError


class RouterError(Exception):
    pass


@dataclass
class Router:
    """Routes records to named pipelines/handlers based on predicate rules."""

    rules: List[Tuple[str, Callable[[dict], bool]]]
    default_route: Optional[str] = None
    schema: Optional[Schema] = None

    def __post_init__(self) -> None:
        if not self.rules:
            raise RouterError("At least one rule must be provided")
        seen: set = set()
        for name, predicate in self.rules:
            if not isinstance(name, str) or not name:
                raise RouterError("Route name must be a non-empty string")
            if name in seen:
                raise RouterError(f"Duplicate route name: {name!r}")
            seen.add(name)
            if not callable(predicate):
                raise RouterError(f"Predicate for route {name!r} must be callable")

    def route(self, records: List[dict]) -> Dict[str, List[dict]]:
        """Apply rules in order; first match wins. Unmatched go to default_route."""
        result: Dict[str, List[dict]] = {name: [] for name, _ in self.rules}
        if self.default_route:
            result.setdefault(self.default_route, [])
        for record in records:
            matched = False
            for name, predicate in self.rules:
                try:
                    if predicate(record):
                        result[name].append(dict(record))
                        matched = True
                        break
                except Exception as exc:
                    raise RouterError(
                        f"Predicate for route {name!r} raised: {exc}"
                    ) from exc
            if not matched:
                if self.default_route is not None:
                    result[self.default_route].append(dict(record))
                # silently drop if no default
        return {k: v for k, v in result.items() if v or k in {n for n, _ in self.rules}}

    def route_names(self) -> List[str]:
        names = [name for name, _ in self.rules]
        if self.default_route and self.default_route not in names:
            names.append(self.default_route)
        return names

    def __repr__(self) -> str:
        names = [n for n, _ in self.rules]
        return f"Router(routes={names}, default_route={self.default_route!r})"

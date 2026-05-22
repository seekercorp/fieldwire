from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from fieldwire.schema import Schema, field_names


class SplitError(Exception):
    pass


@dataclass
class Splitter:
    """Splits a list of records into multiple named buckets based on a predicate map."""

    schema: Schema
    predicates: Dict[str, Callable[[dict], bool]]
    default_bucket: Optional[str] = None

    def __post_init__(self):
        if not self.predicates:
            raise SplitError("At least one predicate must be provided.")
        names = field_names(self.schema)
        for key in self.predicates:
            if not isinstance(key, str) or not key:
                raise SplitError(f"Bucket name must be a non-empty string, got: {key!r}")

    def apply(self, records: List[dict]) -> Dict[str, List[dict]]:
        result: Dict[str, List[dict]] = {name: [] for name in self.predicates}
        if self.default_bucket is not None:
            result.setdefault(self.default_bucket, [])

        for record in records:
            matched = False
            for bucket_name, predicate in self.predicates.items():
                try:
                    if predicate(record):
                        result[bucket_name].append(record)
                        matched = True
                        break
                except Exception as exc:
                    raise SplitError(
                        f"Predicate for bucket '{bucket_name}' raised an error: {exc}"
                    ) from exc
            if not matched:
                if self.default_bucket is not None:
                    result[self.default_bucket].append(record)

        return result

    def __repr__(self) -> str:
        buckets = list(self.predicates.keys())
        return (
            f"Splitter(buckets={buckets}, default_bucket={self.default_bucket!r})"
        )

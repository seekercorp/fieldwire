from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from fieldwire.schema import Schema


class PartitionError(Exception):
    pass


@dataclass
class Partitioner:
    """Splits records into named partitions based on a key function."""

    key_fn: Callable[[dict], str]
    schema: Optional[Schema] = None
    default_partition: Optional[str] = None

    def __post_init__(self) -> None:
        if not callable(self.key_fn):
            raise PartitionError("key_fn must be callable")

    def apply(
        self, records: List[dict]
    ) -> Dict[str, List[dict]]:
        """Partition records into a dict keyed by partition label."""
        result: Dict[str, List[dict]] = {}
        for record in records:
            try:
                key = self.key_fn(record)
            except Exception as exc:
                if self.default_partition is not None:
                    key = self.default_partition
                else:
                    raise PartitionError(
                        f"key_fn raised an error and no default_partition set: {exc}"
                    ) from exc
            if key is None:
                if self.default_partition is not None:
                    key = self.default_partition
                else:
                    raise PartitionError(
                        "key_fn returned None and no default_partition set"
                    )
            result.setdefault(key, []).append(dict(record))
        return result

    def partition_names(self, records: List[dict]) -> List[str]:
        """Return sorted list of partition keys for the given records."""
        return sorted(self.apply(records).keys())

    def __repr__(self) -> str:
        return (
            f"Partitioner(key_fn={self.key_fn.__name__}, "
            f"default_partition={self.default_partition!r})"
        )

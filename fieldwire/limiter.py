from typing import List, Dict, Any, Optional
from fieldwire.schema import Schema


class LimitError(Exception):
    pass


class Limiter:
    """Limits and/or offsets rows in a dataset."""

    def __init__(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        schema: Optional[Schema] = None,
    ):
        if limit is not None and limit < 0:
            raise LimitError(f"limit must be non-negative, got {limit}")
        if offset < 0:
            raise LimitError(f"offset must be non-negative, got {offset}")

        self.limit = limit
        self.offset = offset
        self.schema = schema

    def apply(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return a slice of records applying offset and limit."""
        if not isinstance(records, list):
            raise LimitError("records must be a list")

        sliced = records[self.offset :]
        if self.limit is not None:
            sliced = sliced[: self.limit]
        return sliced

    def __repr__(self) -> str:
        return (
            f"Limiter(limit={self.limit!r}, offset={self.offset!r}, "
            f"schema={self.schema!r})"
        )

from typing import List, Optional
from fieldwire.schema import Schema, get_field


class SortError(Exception):
    pass


class Sorter:
    """Sorts a list of records by one or more fields."""

    def __init__(
        self,
        schema: Schema,
        keys: List[str],
        ascending: Optional[List[bool]] = None,
    ):
        if not keys:
            raise SortError("At least one sort key must be provided.")

        for key in keys:
            field = get_field(schema, key)
            if field is None:
                raise SortError(f"Sort key '{key}' not found in schema.")
            if field.field_type not in (int, float, str):
                raise SortError(
                    f"Field '{key}' has unsortable type '{field.field_type.__name__}'."
                )

        if ascending is None:
            ascending = [True] * len(keys)

        if len(ascending) != len(keys):
            raise SortError(
                "Length of 'ascending' must match length of 'keys'."
            )

        self.schema = schema
        self.keys = keys
        self.ascending = ascending

    def sort(self, records: List[dict]) -> List[dict]:
        """Return a new sorted list of records."""
        if not records:
            return []

        try:
            result = list(records)
            for key, asc in reversed(list(zip(self.keys, self.ascending))):
                result = sorted(
                    result,
                    key=lambda r: (r.get(key) is None, r.get(key)),
                    reverse=not asc,
                )
            return result
        except TypeError as exc:
            raise SortError(f"Failed to sort records: {exc}") from exc

    def __repr__(self) -> str:
        pairs = ", ".join(
            f"{k} {'ASC' if a else 'DESC'}"
            for k, a in zip(self.keys, self.ascending)
        )
        return f"Sorter(keys=[{pairs}])"

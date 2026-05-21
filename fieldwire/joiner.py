from typing import Any, Dict, List, Optional
from fieldwire.schema import Schema, field_names


class JoinError(Exception):
    pass


class Joiner:
    """
    Joins two lists of records on a common key field.
    Supports inner, left, and right join types.
    """

    SUPPORTED_JOINS = ("inner", "left", "right")

    def __init__(
        self,
        left_key: str,
        right_key: str,
        join_type: str = "inner",
        left_schema: Optional[Schema] = None,
        right_schema: Optional[Schema] = None,
    ):
        if join_type not in self.SUPPORTED_JOINS:
            raise JoinError(
                f"Unsupported join type '{join_type}'. "
                f"Choose from: {self.SUPPORTED_JOINS}"
            )
        self.left_key = left_key
        self.right_key = right_key
        self.join_type = join_type
        self.left_schema = left_schema
        self.right_schema = right_schema

    def _validate_key(self, records: List[Dict], key: str, side: str) -> None:
        if records and key not in records[0]:
            raise JoinError(
                f"Key '{key}' not found in {side} records. "
                f"Available fields: {list(records[0].keys())}"
            )

    def join(
        self, left: List[Dict[str, Any]], right: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if not left and not right:
            return []

        if left:
            self._validate_key(left, self.left_key, "left")
        if right:
            self._validate_key(right, self.right_key, "right")

        right_index: Dict[Any, List[Dict]] = {}
        for record in right:
            key_val = record[self.right_key]
            right_index.setdefault(key_val, []).append(record)

        results: List[Dict[str, Any]] = []

        matched_right_keys = set()

        for left_record in left:
            key_val = left_record[self.left_key]
            right_matches = right_index.get(key_val, [])

            if right_matches:
                for right_record in right_matches:
                    merged = {**left_record, **right_record}
                    results.append(merged)
                    matched_right_keys.add(key_val)
            elif self.join_type == "left":
                right_nulls = {k: None for k in (right[0].keys() if right else [])}
                results.append({**left_record, **right_nulls})

        if self.join_type == "right":
            for right_record in right:
                key_val = right_record[self.right_key]
                if key_val not in matched_right_keys:
                    left_nulls = {k: None for k in (left[0].keys() if left else [])}
                    results.append({**left_nulls, **right_record})

        return results

    def __repr__(self) -> str:
        return (
            f"Joiner(left_key={self.left_key!r}, right_key={self.right_key!r}, "
            f"join_type={self.join_type!r})"
        )

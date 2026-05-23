from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from fieldwire.schema import Schema, field_names


class CrossError(Exception):
    """Raised when a cross-join operation fails."""


@dataclass
class Crosser:
    """Produces the Cartesian product of two record lists.

    Parameters
    ----------
    left_schema:  Schema for the left records (optional).
    right_schema: Schema for the right records (optional).
    left_prefix:  Prefix applied to left field names on collision.
    right_prefix: Prefix applied to right field names on collision.
    """

    left_schema: Optional[Schema] = None
    right_schema: Optional[Schema] = None
    left_prefix: str = "left_"
    right_prefix: str = "right_"

    def __post_init__(self) -> None:
        if not self.left_prefix and not self.right_prefix:
            raise CrossError("At least one of left_prefix or right_prefix must be non-empty.")

    def _resolve_keys(
        self,
        left: List[Dict[str, Any]],
        right: List[Dict[str, Any]],
    ) -> tuple[set[str], set[str]]:
        left_keys: set[str] = set()
        right_keys: set[str] = set()
        if self.left_schema:
            left_keys = set(field_names(self.left_schema))
        elif left:
            left_keys = set(left[0].keys())
        if self.right_schema:
            right_keys = set(field_names(self.right_schema))
        elif right:
            right_keys = set(right[0].keys())
        return left_keys, right_keys

    def apply(
        self,
        left: List[Dict[str, Any]],
        right: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Return every combination of rows from *left* and *right*."""
        if not left or not right:
            return []

        left_keys, right_keys = self._resolve_keys(left, right)
        collisions = left_keys & right_keys

        results: List[Dict[str, Any]] = []
        for l_row in left:
            for r_row in right:
                merged: Dict[str, Any] = {}
                for k, v in l_row.items():
                    merged[self.left_prefix + k if k in collisions else k] = v
                for k, v in r_row.items():
                    merged[self.right_prefix + k if k in collisions else k] = v
                results.append(merged)
        return results

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Crosser(left_prefix={self.left_prefix!r}, "
            f"right_prefix={self.right_prefix!r})"
        )

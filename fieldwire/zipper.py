from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from fieldwire.schema import Schema, field_names


class ZipError(Exception):
    pass


@dataclass
class Zipper:
    """Zips multiple lists of records together by position, merging fields row-by-row."""

    schemas: Optional[List[Schema]] = None
    fill_value: Any = None

    def __post_init__(self):
        if self.schemas is not None:
            if len(self.schemas) < 2:
                raise ZipError("At least two schemas are required for zipping.")
            all_fields = []
            for schema in self.schemas:
                all_fields.extend(field_names(schema))
            if len(all_fields) != len(set(all_fields)):
                raise ZipError(
                    "Schemas contain overlapping field names. Use Renamer to disambiguate."
                )

    def apply(self, *record_lists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(record_lists) < 2:
            raise ZipError("apply() requires at least two record lists.")

        max_len = max(len(lst) for lst in record_lists)

        result = []
        for i in range(max_len):
            merged: Dict[str, Any] = {}
            for lst in record_lists:
                if i < len(lst):
                    row = lst[i]
                    if not isinstance(row, dict):
                        raise ZipError(f"Expected dict at index {i}, got {type(row).__name__}.")
                    overlapping = set(merged.keys()) & set(row.keys())
                    if overlapping:
                        raise ZipError(
                            f"Overlapping field(s) detected during zip: {overlapping}. "
                            "Use Renamer to disambiguate before zipping."
                        )
                    merged.update(row)
                else:
                    # Pad with fill_value for missing rows in shorter lists
                    if self.schemas is not None:
                        idx = list(record_lists).index(lst)
                        for fname in field_names(self.schemas[idx]):
                            if fname not in merged:
                                merged[fname] = self.fill_value
            result.append(merged)

        return result

    def __repr__(self) -> str:
        schema_info = f", schemas={len(self.schemas)}" if self.schemas else ""
        return f"Zipper(fill_value={self.fill_value!r}{schema_info})"

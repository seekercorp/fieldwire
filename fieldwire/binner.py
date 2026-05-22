from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from fieldwire.schema import Schema, FieldSchema


class BinError(Exception):
    pass


@dataclass
class Binner:
    """Assigns records to named bins based on numeric field thresholds."""

    field: str
    bins: List[float]
    labels: List[str]
    output_field: str = "bin"
    schema: Optional[Schema] = None

    def __post_init__(self):
        if len(self.labels) != len(self.bins) + 1:
            raise BinError(
                f"Expected {len(self.bins) + 1} labels for {len(self.bins)} "
                f"bin edges, got {len(self.labels)}."
            )
        if self.bins != sorted(self.bins):
            raise BinError("Bin edges must be in ascending order.")
        if self.schema is not None:
            field_names = [f.name for f in self.schema.fields]
            if self.field not in field_names:
                raise BinError(
                    f"Field '{self.field}' not found in schema."
                )

    def _assign_bin(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        for i, edge in enumerate(self.bins):
            if value < edge:
                return self.labels[i]
        return self.labels[-1]

    def apply(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = []
        for record in records:
            if self.field not in record:
                raise BinError(
                    f"Field '{self.field}' missing from record: {record}"
                )
            new_record = dict(record)
            new_record[self.output_field] = self._assign_bin(record[self.field])
            result.append(new_record)
        return result

    def output_schema(self) -> Optional[Schema]:
        if self.schema is None:
            return None
        new_fields = list(self.schema.fields) + [
            FieldSchema(name=self.output_field, type=str, nullable=True)
        ]
        return Schema(fields=new_fields)

    def __repr__(self) -> str:
        return (
            f"Binner(field={self.field!r}, bins={self.bins}, "
            f"labels={self.labels}, output_field={self.output_field!r})"
        )

from dataclasses import dataclass, field
from typing import Dict, List
from fieldwire.schema import Schema, FieldSchema


class RenameError(Exception):
    pass


@dataclass
class Renamer:
    """Renames fields in records according to a mapping of old_name -> new_name."""

    schema: Schema
    mapping: Dict[str, str]
    _output_schema: Schema = field(init=False, repr=False)

    def __post_init__(self):
        existing_names = {f.name for f in self.schema.fields}
        for old_name in self.mapping:
            if old_name not in existing_names:
                raise RenameError(
                    f"Field '{old_name}' not found in schema. "
                    f"Available fields: {sorted(existing_names)}"
                )
        new_names = list(self.mapping.values())
        if len(new_names) != len(set(new_names)):
            raise RenameError("Duplicate target field names in rename mapping.")
        renamed_fields = []
        for f in self.schema.fields:
            new_name = self.mapping.get(f.name, f.name)
            renamed_fields.append(FieldSchema(name=new_name, type=f.type, nullable=f.nullable))
        self._output_schema = Schema(fields=renamed_fields)

    @property
    def output_schema(self) -> Schema:
        return self._output_schema

    def apply(self, records: List[dict]) -> List[dict]:
        """Return a new list of records with fields renamed according to the mapping."""
        result = []
        for record in records:
            new_record = {}
            for key, value in record.items():
                new_key = self.mapping.get(key, key)
                new_record[new_key] = value
            result.append(new_record)
        return result

    def __repr__(self) -> str:
        return f"Renamer(mapping={self.mapping})"

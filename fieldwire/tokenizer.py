from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from fieldwire.schema import Schema, get_field


class TokenizeError(Exception):
    pass


def _default_tokenizer(text: str) -> List[str]:
    return text.lower().split()


@dataclass
class Tokenizer:
    """Split a string field into a list of tokens and store in a new field."""

    input_field: str
    output_field: str
    tokenize_fn: Callable[[str], List[str]] = field(default=_default_tokenizer)
    schema: Optional[Schema] = field(default=None)

    def __post_init__(self) -> None:
        if self.schema is not None:
            field_names = [f.name for f in self.schema.fields]
            if self.input_field not in field_names:
                raise TokenizeError(
                    f"Input field '{self.input_field}' not found in schema."
                )
            src = get_field(self.schema, self.input_field)
            if src.dtype is not str:
                raise TokenizeError(
                    f"Input field '{self.input_field}' must be of type str, "
                    f"got {src.dtype}."
                )
            if self.output_field in field_names:
                raise TokenizeError(
                    f"Output field '{self.output_field}' already exists in schema."
                )

    def apply(self, records: List[dict]) -> List[dict]:
        out = []
        for i, record in enumerate(records):
            if self.input_field not in record:
                raise TokenizeError(
                    f"Record {i} is missing field '{self.input_field}'."
                )
            value = record[self.input_field]
            if value is None:
                tokens: Optional[List[str]] = None
            elif not isinstance(value, str):
                raise TokenizeError(
                    f"Expected str for field '{self.input_field}' in record {i}, "
                    f"got {type(value).__name__}."
                )
            else:
                try:
                    tokens = self.tokenize_fn(value)
                except Exception as exc:
                    raise TokenizeError(
                        f"Tokenizer function raised an error on record {i}: {exc}"
                    ) from exc
            new_record = dict(record)
            new_record[self.output_field] = tokens
            out.append(new_record)
        return out

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Tokenizer(input_field={self.input_field!r}, "
            f"output_field={self.output_field!r})"
        )

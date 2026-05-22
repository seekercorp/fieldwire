from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from typing import Any, Literal

from fieldwire.schema import Schema, validate


class DecodeError(Exception):
    pass


@dataclass
class Decoder:
    """Deserialise JSON or CSV text into a list of validated records."""

    format: Literal["json", "csv"] = "json"
    csv_delimiter: str = ","
    schema: Schema | None = None

    def __post_init__(self) -> None:
        if self.format not in ("json", "csv"):
            raise DecodeError(f"Unsupported format: {self.format!r}. Choose 'json' or 'csv'.")

    def decode(self, text: str) -> list[dict[str, Any]]:
        """Parse *text* and return a list of records, validating against schema if set."""
        if self.format == "json":
            records = self._decode_json(text)
        else:
            records = self._decode_csv(text)
        if self.schema is not None:
            for i, record in enumerate(records):
                for fs in self.schema.fields:
                    try:
                        validate(fs, record.get(fs.name))
                    except (TypeError, ValueError) as exc:
                        raise DecodeError(f"Validation failed at record {i}, field {fs.name!r}: {exc}") from exc
        return records

    def _decode_json(self, text: str) -> list[dict[str, Any]]:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise DecodeError(f"Invalid JSON: {exc}") from exc
        if not isinstance(data, list):
            raise DecodeError("JSON root must be an array of objects.")
        return data

    def _decode_csv(self, text: str) -> list[dict[str, Any]]:
        try:
            reader = csv.DictReader(io.StringIO(text), delimiter=self.csv_delimiter)
            return [dict(row) for row in reader]
        except csv.Error as exc:
            raise DecodeError(f"CSV parsing failed: {exc}") from exc

    def __repr__(self) -> str:  # pragma: no cover
        return f"Decoder(format={self.format!r}, delimiter={self.csv_delimiter!r})"

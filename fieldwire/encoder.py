from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from typing import Any, Literal

from fieldwire.schema import Schema


class EncodeError(Exception):
    pass


@dataclass
class Encoder:
    """Serialise a list of records to JSON or CSV text."""

    format: Literal["json", "csv"] = "json"
    indent: int | None = None  # JSON only
    csv_delimiter: str = ","  # CSV only
    schema: Schema | None = None

    def __post_init__(self) -> None:
        if self.format not in ("json", "csv"):
            raise EncodeError(f"Unsupported format: {self.format!r}. Choose 'json' or 'csv'.")

    def encode(self, records: list[dict[str, Any]]) -> str:
        """Return a string representation of *records* in the chosen format."""
        if not isinstance(records, list):
            raise EncodeError("records must be a list of dicts.")
        if self.format == "json":
            return self._encode_json(records)
        return self._encode_csv(records)

    def _encode_json(self, records: list[dict[str, Any]]) -> str:
        try:
            return json.dumps(records, indent=self.indent, default=str)
        except (TypeError, ValueError) as exc:
            raise EncodeError(f"JSON serialisation failed: {exc}") from exc

    def _encode_csv(self, records: list[dict[str, Any]]) -> str:
        if not records:
            return ""
        fieldnames = list(records[0].keys())
        buf = io.StringIO()
        writer = csv.DictWriter(
            buf,
            fieldnames=fieldnames,
            delimiter=self.csv_delimiter,
            lineterminator="\n",
        )
        writer.writeheader()
        try:
            writer.writerows(records)
        except (csv.Error, ValueError) as exc:
            raise EncodeError(f"CSV serialisation failed: {exc}") from exc
        return buf.getvalue()

    def __repr__(self) -> str:  # pragma: no cover
        return f"Encoder(format={self.format!r}, delimiter={self.csv_delimiter!r})"

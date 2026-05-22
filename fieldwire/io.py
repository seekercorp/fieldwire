"""Convenience façade combining Encoder and Decoder for round-trip I/O."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from fieldwire.decoder import Decoder
from fieldwire.encoder import Encoder
from fieldwire.schema import Schema


@dataclass
class RecordIO:
    """High-level helper for encoding and decoding record lists.

    Example::

        io = RecordIO(format="csv")
        csv_text = io.dump(records)
        records_back = io.load(csv_text)
    """

    format: Literal["json", "csv"] = "json"
    schema: Schema | None = None
    indent: int | None = None
    csv_delimiter: str = ","

    def dump(self, records: list[dict[str, Any]]) -> str:
        """Serialise *records* to a string."""
        encoder = Encoder(
            format=self.format,
            indent=self.indent,
            csv_delimiter=self.csv_delimiter,
            schema=self.schema,
        )
        return encoder.encode(records)

    def load(self, text: str) -> list[dict[str, Any]]:
        """Deserialise *text* back into a list of records."""
        decoder = Decoder(
            format=self.format,
            csv_delimiter=self.csv_delimiter,
            schema=self.schema,
        )
        return decoder.decode(text)

    def roundtrip(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Encode then immediately decode *records* — useful for testing."""
        return self.load(self.dump(records))

    def __repr__(self) -> str:  # pragma: no cover
        return f"RecordIO(format={self.format!r}, schema={self.schema})"

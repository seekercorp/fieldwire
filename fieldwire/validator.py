from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from fieldwire.schema import Schema, field_names


class ValidateError(Exception):
    pass


@dataclass
class Validator:
    """Applies user-defined predicate rules to records and reports violations."""

    schema: Optional[Schema] = None
    rules: Dict[str, Callable[[object], bool]] = field(default_factory=dict)
    raise_on_fail: bool = False

    def __post_init__(self) -> None:
        if self.schema is not None:
            known = set(field_names(self.schema))
            for fname in self.rules:
                if fname not in known:
                    raise ValidateError(
                        f"Rule targets unknown field '{fname}' not in schema."
                    )

    def validate(
        self, records: List[Dict]
    ) -> Dict[str, object]:
        """
        Validate *records* against all registered rules.

        Returns a report dict with keys:
          - 'total': int
          - 'passed': int
          - 'failed': int
          - 'violations': list of {'index': int, 'field': str, 'value': any}
        """
        violations: List[Dict] = []

        for idx, record in enumerate(records):
            for fname, predicate in self.rules.items():
                value = record.get(fname)
                try:
                    ok = predicate(value)
                except Exception as exc:  # noqa: BLE001
                    ok = False
                    if self.raise_on_fail:
                        raise ValidateError(
                            f"Rule for field '{fname}' raised an exception "
                            f"on record {idx}: {exc}"
                        ) from exc
                if not ok:
                    violations.append(
                        {"index": idx, "field": fname, "value": value}
                    )
                    if self.raise_on_fail:
                        raise ValidateError(
                            f"Validation failed for field '{fname}' "
                            f"at record {idx}: value={value!r}"
                        )

        total = len(records)
        failed_indices = {v["index"] for v in violations}
        return {
            "total": total,
            "passed": total - len(failed_indices),
            "failed": len(failed_indices),
            "violations": violations,
        }

    def __repr__(self) -> str:  # pragma: no cover
        rule_keys = list(self.rules.keys())
        return (
            f"Validator(rules={rule_keys}, raise_on_fail={self.raise_on_fail})"
        )

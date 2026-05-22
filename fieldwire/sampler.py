from dataclasses import dataclass
from typing import List, Optional
import random
from fieldwire.schema import Schema


class SampleError(Exception):
    pass


@dataclass
class Sampler:
    """Randomly samples rows from a dataset."""

    n: Optional[int] = None
    fraction: Optional[float] = None
    seed: Optional[int] = None

    def __post_init__(self):
        if self.n is None and self.fraction is None:
            raise SampleError("Either 'n' or 'fraction' must be specified.")
        if self.n is not None and self.fraction is not None:
            raise SampleError("Only one of 'n' or 'fraction' may be specified.")
        if self.n is not None and self.n < 0:
            raise SampleError("'n' must be a non-negative integer.")
        if self.fraction is not None and not (0.0 <= self.fraction <= 1.0):
            raise SampleError("'fraction' must be between 0.0 and 1.0.")

    def apply(self, records: List[dict], schema: Optional[Schema] = None) -> List[dict]:
        rng = random.Random(self.seed)
        if self.n is not None:
            k = min(self.n, len(records))
            return rng.sample(records, k)
        count = round(len(records) * self.fraction)
        return rng.sample(records, count)

    def __repr__(self) -> str:
        if self.n is not None:
            return f"Sampler(n={self.n}, seed={self.seed!r})"
        return f"Sampler(fraction={self.fraction}, seed={self.seed!r})"

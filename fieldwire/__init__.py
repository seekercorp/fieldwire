"""fieldwire — typed data pipelines with automatic schema inference and validation."""

from fieldwire.schema import FieldSchema, Schema, validate, field_names, get_field
from fieldwire.inference import infer_field_schema, infer_schema
from fieldwire.pipeline import Step, PipelineError
from fieldwire.transform import FieldTransform, TransformError
from fieldwire.aggregator import Aggregator, AggregationError
from fieldwire.groupby import GroupBy, GroupByError
from fieldwire.joiner import Joiner, JoinError
from fieldwire.sorter import Sorter, SortError
from fieldwire.filter import Filter, FilterError
from fieldwire.limiter import Limiter, LimitError
from fieldwire.renamer import Renamer, RenameError
from fieldwire.deduplicator import Deduplicator, DeduplicateError
from fieldwire.sampler import Sampler, SampleError

__all__ = [
    "FieldSchema",
    "Schema",
    "validate",
    "field_names",
    "get_field",
    "infer_field_schema",
    "infer_schema",
    "Step",
    "PipelineError",
    "FieldTransform",
    "TransformError",
    "Aggregator",
    "AggregationError",
    "GroupBy",
    "GroupByError",
    "Joiner",
    "JoinError",
    "Sorter",
    "SortError",
    "Filter",
    "FilterError",
    "Limiter",
    "LimitError",
    "Renamer",
    "RenameError",
    "Deduplicator",
    "DeduplicateError",
    "Sampler",
    "SampleError",
]

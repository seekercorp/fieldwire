"""Fieldwire: typed data pipelines with automatic schema inference and validation."""

from fieldwire.schema import FieldSchema, Schema, validate, field_names, get_field
from fieldwire.inference import infer_field_schema, infer_schema
from fieldwire.pipeline import PipelineError, Step
from fieldwire.transform import TransformError, FieldTransform
from fieldwire.aggregator import AggregationError, Aggregator
from fieldwire.groupby import GroupByError, GroupBy
from fieldwire.joiner import JoinError, Joiner
from fieldwire.sorter import SortError, Sorter
from fieldwire.filter import FilterError, Filter
from fieldwire.limiter import LimitError, Limiter
from fieldwire.renamer import RenameError, Renamer
from fieldwire.deduplicator import DeduplicateError, Deduplicator
from fieldwire.sampler import SampleError, Sampler
from fieldwire.caster import CastError, Caster
from fieldwire.flattener import FlattenError, Flattener

__all__ = [
    # Schema
    "FieldSchema",
    "Schema",
    "validate",
    "field_names",
    "get_field",
    # Inference
    "infer_field_schema",
    "infer_schema",
    # Pipeline
    "PipelineError",
    "Step",
    # Transform
    "TransformError",
    "FieldTransform",
    # Aggregator
    "AggregationError",
    "Aggregator",
    # GroupBy
    "GroupByError",
    "GroupBy",
    # Joiner
    "JoinError",
    "Joiner",
    # Sorter
    "SortError",
    "Sorter",
    # Filter
    "FilterError",
    "Filter",
    # Limiter
    "LimitError",
    "Limiter",
    # Renamer
    "RenameError",
    "Renamer",
    # Deduplicator
    "DeduplicateError",
    "Deduplicator",
    # Sampler
    "SampleError",
    "Sampler",
    # Caster
    "CastError",
    "Caster",
    # Flattener
    "FlattenError",
    "Flattener",
]

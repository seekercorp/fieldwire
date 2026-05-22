"""fieldwire — typed data pipelines with automatic schema inference and validation."""

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
from fieldwire.pivotter import PivotError, Pivotter
from fieldwire.unpivotter import UnpivotError, Unpivotter

__all__ = [
    # schema
    "FieldSchema",
    "Schema",
    "validate",
    "field_names",
    "get_field",
    # inference
    "infer_field_schema",
    "infer_schema",
    # pipeline
    "PipelineError",
    "Step",
    # transform
    "TransformError",
    "FieldTransform",
    # aggregator
    "AggregationError",
    "Aggregator",
    # groupby
    "GroupByError",
    "GroupBy",
    # joiner
    "JoinError",
    "Joiner",
    # sorter
    "SortError",
    "Sorter",
    # filter
    "FilterError",
    "Filter",
    # limiter
    "LimitError",
    "Limiter",
    # renamer
    "RenameError",
    "Renamer",
    # deduplicator
    "DeduplicateError",
    "Deduplicator",
    # sampler
    "SampleError",
    "Sampler",
    # caster
    "CastError",
    "Caster",
    # flattener
    "FlattenError",
    "Flattener",
    # pivotter
    "PivotError",
    "Pivotter",
    # unpivotter
    "UnpivotError",
    "Unpivotter",
]

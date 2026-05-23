"""fieldwire — typed data pipeline library."""

from fieldwire.schema import FieldSchema, Schema, validate, field_names, get_field
from fieldwire.pipeline import PipelineError, Step
from fieldwire.inference import infer_field_schema, infer_schema
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
from fieldwire.window import WindowError, Window
from fieldwire.roller import RollerError, Roller
from fieldwire.splitter import SplitError, Splitter
from fieldwire.merger import MergeError, Merger
from fieldwire.filler import FillError, Filler
from fieldwire.normalizer import NormalizeError, Normalizer
from fieldwire.encoder import EncodeError, Encoder
from fieldwire.decoder import DecodeError, Decoder
from fieldwire.io import RecordIO
from fieldwire.profiler import ProfileError, FieldProfile, Profiler
from fieldwire.validator import ValidateError, Validator
from fieldwire.hasher import HashError, Hasher
from fieldwire.binner import BinError, Binner
from fieldwire.zipper import ZipError, Zipper
from fieldwire.scorer import ScoreError, Scorer
from fieldwire.differ import DiffError, DiffResult, Differ
from fieldwire.changelog import ChangelogError, ChangelogEntry, Changelog
from fieldwire.forecaster import ForecastError, Forecaster
from fieldwire.annotator import AnnotateError, Annotator
from fieldwire.clipper import ClipError, Clipper
from fieldwire.reshaper import ReshapeError, Reshaper
from fieldwire.imputer import ImputeError, Imputer
from fieldwire.outlier import OutlierError, Outlier
from fieldwire.detector import DetectError, AnomalyReport, Detector
from fieldwire.partitioner import PartitionError, Partitioner
from fieldwire.router import RouterError, Router

__all__ = [
    # schema
    "FieldSchema", "Schema", "validate", "field_names", "get_field",
    # pipeline
    "PipelineError", "Step",
    # inference
    "infer_field_schema", "infer_schema",
    # transform
    "TransformError", "FieldTransform",
    # aggregator
    "AggregationError", "Aggregator",
    # groupby
    "GroupByError", "GroupBy",
    # joiner
    "JoinError", "Joiner",
    # sorter
    "SortError", "Sorter",
    # filter
    "FilterError", "Filter",
    # limiter
    "LimitError", "Limiter",
    # renamer
    "RenameError", "Renamer",
    # deduplicator
    "DeduplicateError", "Deduplicator",
    # sampler
    "SampleError", "Sampler",
    # caster
    "CastError", "Caster",
    # flattener
    "FlattenError", "Flattener",
    # pivotter
    "PivotError", "Pivotter",
    # unpivotter
    "UnpivotError", "Unpivotter",
    # window
    "WindowError", "Window",
    # roller
    "RollerError", "Roller",
    # splitter
    "SplitError", "Splitter",
    # merger
    "MergeError", "Merger",
    # filler
    "FillError", "Filler",
    # normalizer
    "NormalizeError", "Normalizer",
    # encoder / decoder
    "EncodeError", "Encoder",
    "DecodeError", "Decoder",
    # io
    "RecordIO",
    # profiler
    "ProfileError", "FieldProfile", "Profiler",
    # validator
    "ValidateError", "Validator",
    # hasher
    "HashError", "Hasher",
    # binner
    "BinError", "Binner",
    # zipper
    "ZipError", "Zipper",
    # scorer
    "ScoreError", "Scorer",
    # differ
    "DiffError", "DiffResult", "Differ",
    # changelog
    "ChangelogError", "ChangelogEntry", "Changelog",
    # forecaster
    "ForecastError", "Forecaster",
    # annotator
    "AnnotateError", "Annotator",
    # clipper
    "ClipError", "Clipper",
    # reshaper
    "ReshapeError", "Reshaper",
    # imputer
    "ImputeError", "Imputer",
    # outlier
    "OutlierError", "Outlier",
    # detector
    "DetectError", "AnomalyReport", "Detector",
    # partitioner
    "PartitionError", "Partitioner",
    # router
    "RouterError", "Router",
]

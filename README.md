# fieldwire

**fieldwire** is a Python library for building typed data pipelines with automatic schema inference and validation.

## Features

- `Schema` / `FieldSchema` — define and validate typed record schemas
- `infer_schema` — automatically infer a schema from sample records
- `FieldTransform` — apply per-field transformation functions
- `Aggregator` — compute sum, mean, count, min, max over record lists
- `GroupBy` — group records by a key and aggregate
- `Joiner` — inner / left / right join two record lists
- `Sorter` — sort records by one or more keys
- `Filter` — keep records matching a predicate
- `Limiter` — slice records with limit + offset
- `Renamer` — rename fields
- `Deduplicator` — remove duplicate records by key
- `Sampler` — random sampling by count or fraction
- `Caster` — cast field values to a target type
- `Flattener` — flatten a nested dict field into top-level fields
- `Pivotter` — pivot long-format records to wide format
- `Unpivotter` — unpivot wide-format records to long format
- `Window` — rolling window calculations
- `Roller` — multi-spec rolling aggregations
- `Splitter` — route records into named buckets by predicate
- `Merger` — merge multiple record lists
- `Filler` — fill None values (explicit, forward-fill, backward-fill)
- `Normalizer` — min-max or z-score normalisation
- `Encoder` / `Decoder` — JSON and CSV serialisation
- `RecordIO` — dump / load / roundtrip helpers
- `Profiler` — per-field statistics (null rate, unique count, min/max, …)
- `Validator` — rule-based record validation with violation reporting
- `Hasher` — deterministic row hashing (MD5 / SHA256)
- `Binner` — assign numeric values to labelled bins
- `Zipper` — zip multiple record lists row-by-row
- `Scorer` — weighted rule-based record scoring
- `Differ` — diff two snapshots of record lists
- `Changelog` — track successive snapshots and their diffs
- `Forecaster` — append forecast columns via user-supplied models
- `Annotator` — add constant or computed annotation fields
- `Clipper` — clip numeric field values to [lower, upper] bounds
- `Reshaper` — reorder / project fields
- `Imputer` — impute missing values (mean, median, mode, constant)
- `Outlier` — detect and handle outliers (IQR, z-score, clip, remove)
- `Detector` — anomaly detection reports (null, range, z-score checks)
- `Partitioner` — split records into named partitions by a key function
- `Router` — route records to named outputs by ordered predicate rules
- `Truncator` — truncate string fields to a maximum length
- `Tokenizer` — tokenize string fields into lists of tokens
- `Embedder` — embed field values into numeric vectors via a callable
- `Step` / `Pipeline` — compose the above into end-to-end pipelines

## Installation

```bash
pip install fieldwire
```

## Quick start

```python
from fieldwire import infer_schema, Filter, Sorter, Embedder

records = [
    {"id": 1, "text": "hello world"},
    {"id": 2, "text": "foo bar baz"},
    {"id": 3, "text": "spam"},
]

schema = infer_schema(records)

def bag_of_chars(value):
    return [float(ord(c)) for c in (value or "")]

embedder = Embedder(
    input_field="text",
    output_field="vec",
    embed_fn=bag_of_chars,
    schema=schema,
)

result = embedder.apply(records)
for row in result:
    print(row["id"], len(row["vec"]))
```

## License

MIT

# fieldwire

Python library for building typed data pipelines with automatic schema inference and validation.

---

## Installation

```bash
pip install fieldwire
```

## Usage

```python
from fieldwire import Pipeline, Schema

# Define a schema or let fieldwire infer it automatically
pipeline = Pipeline.from_data([
    {"name": "Alice", "age": 30, "score": 98.5},
    {"name": "Bob",   "age": 25, "score": 87.0},
])

# Inspect the inferred schema
print(pipeline.schema)
# Schema(name=str, age=int, score=float)

# Add a validation step and transform the data
result = (
    pipeline
    .validate(lambda row: row["age"] >= 0)
    .transform(lambda row: {**row, "grade": "A" if row["score"] >= 90 else "B"})
    .run()
)

print(result.to_records())
# [{'name': 'Alice', 'age': 30, 'score': 98.5, 'grade': 'A'},
#  {'name': 'Bob',   'age': 25, 'score': 87.0, 'grade': 'B'}]
```

You can also define schemas explicitly for strict validation:

```python
from fieldwire import Schema, Field

schema = Schema(
    name=Field(str, required=True),
    age=Field(int, min=0, max=120),
    score=Field(float, min=0.0, max=100.0),
)

pipeline = Pipeline(schema=schema).load("data.csv").validate().run()
```

## Features

- Automatic schema inference from raw data
- Explicit schema definitions with field-level constraints
- Chainable pipeline API
- CSV, JSON, and dict input support
- Clear validation error reporting

## License

[MIT](LICENSE)
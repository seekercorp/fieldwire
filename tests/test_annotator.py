import pytest
from fieldwire.annotator import Annotator, AnnotateError
from fieldwire.schema import Schema, FieldSchema


def make_schema(*names_types):
    fields = [FieldSchema(name=n, type=t, nullable=False) for n, t in names_types]
    return Schema(fields=fields)


def test_annotator_adds_new_field():
    records = [{"value": 10}, {"value": 20}]
    ann = Annotator(annotations={"doubled": lambda r: r["value"] * 2})
    result = ann.apply(records)
    assert result[0]["doubled"] == 20
    assert result[1]["doubled"] == 40


def test_annotator_does_not_mutate_original():
    records = [{"value": 5}]
    ann = Annotator(annotations={"extra": lambda r: r["value"] + 1})
    result = ann.apply(records)
    assert "extra" not in records[0]
    assert result[0]["extra"] == 6


def test_annotator_multiple_annotations():
    records = [{"x": 3, "y": 4}]
    ann = Annotator(annotations={
        "sum": lambda r: r["x"] + r["y"],
        "product": lambda r: r["x"] * r["y"],
    })
    result = ann.apply(records)
    assert result[0]["sum"] == 7
    assert result[0]["product"] == 12


def test_annotator_existing_field_raises_without_overwrite():
    records = [{"value": 1, "tag": "old"}]
    ann = Annotator(annotations={"tag": lambda r: "new"})
    with pytest.raises(AnnotateError, match="already present"):
        ann.apply(records)


def test_annotator_overwrite_replaces_field():
    records = [{"value": 1, "tag": "old"}]
    ann = Annotator(annotations={"tag": lambda r: "new"}, overwrite=True)
    result = ann.apply(records)
    assert result[0]["tag"] == "new"


def test_annotator_fn_exception_raises_annotate_error():
    records = [{"value": None}]
    ann = Annotator(annotations={"bad": lambda r: r["value"] + 1})
    with pytest.raises(AnnotateError, match="failed on record"):
        ann.apply(records)


def test_annotator_empty_annotations_raises():
    with pytest.raises(AnnotateError, match="must not be empty"):
        Annotator(annotations={})


def test_annotator_schema_conflict_raises():
    schema = make_schema(("value", int), ("label", str))
    with pytest.raises(AnnotateError, match="already exists in schema"):
        Annotator(annotations={"label": lambda r: "x"}, schema=schema)


def test_annotator_schema_conflict_allowed_with_overwrite():
    schema = make_schema(("value", int), ("label", str))
    ann = Annotator(annotations={"label": lambda r: "new"}, schema=schema, overwrite=True)
    result = ann.apply([{"value": 1, "label": "old"}])
    assert result[0]["label"] == "new"


def test_annotator_preserves_existing_fields():
    records = [{"a": 1, "b": 2}]
    ann = Annotator(annotations={"c": lambda r: r["a"] + r["b"]})
    result = ann.apply(records)
    assert result[0]["a"] == 1
    assert result[0]["b"] == 2
    assert result[0]["c"] == 3


def test_annotator_repr():
    ann = Annotator(annotations={"score": lambda r: 0}, overwrite=False)
    assert "Annotator" in repr(ann)
    assert "score" in repr(ann)

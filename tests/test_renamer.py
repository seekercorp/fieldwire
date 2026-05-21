import pytest
from fieldwire.schema import Schema, FieldSchema
from fieldwire.renamer import Renamer, RenameError


def make_schema():
    return Schema(fields=[
        FieldSchema(name="id", type=int, nullable=False),
        FieldSchema(name="val", type=float, nullable=True),
        FieldSchema(name="label", type=str, nullable=False),
    ])


def test_rename_single_field():
    schema = make_schema()
    renamer = Renamer(schema=schema, mapping={"val": "value"})
    records = [{"id": 1, "val": 3.14, "label": "a"}]
    result = renamer.apply(records)
    assert result == [{"id": 1, "value": 3.14, "label": "a"}]


def test_rename_multiple_fields():
    schema = make_schema()
    renamer = Renamer(schema=schema, mapping={"id": "identifier", "label": "tag"})
    records = [{"id": 2, "val": 1.0, "label": "b"}]
    result = renamer.apply(records)
    assert result == [{"identifier": 2, "val": 1.0, "tag": "b"}]


def test_rename_does_not_mutate_original():
    schema = make_schema()
    renamer = Renamer(schema=schema, mapping={"id": "new_id"})
    original = {"id": 10, "val": 0.5, "label": "c"}
    records = [original]
    renamer.apply(records)
    assert "id" in original
    assert "new_id" not in original


def test_rename_empty_mapping():
    schema = make_schema()
    renamer = Renamer(schema=schema, mapping={})
    records = [{"id": 1, "val": 2.0, "label": "x"}]
    result = renamer.apply(records)
    assert result == [{"id": 1, "val": 2.0, "label": "x"}]


def test_rename_empty_records():
    schema = make_schema()
    renamer = Renamer(schema=schema, mapping={"id": "new_id"})
    result = renamer.apply([])
    assert result == []


def test_output_schema_updated():
    schema = make_schema()
    renamer = Renamer(schema=schema, mapping={"val": "value"})
    out_names = [f.name for f in renamer.output_schema.fields]
    assert "value" in out_names
    assert "val" not in out_names
    assert "id" in out_names
    assert "label" in out_names


def test_output_schema_preserves_types():
    schema = make_schema()
    renamer = Renamer(schema=schema, mapping={"val": "value"})
    field_map = {f.name: f for f in renamer.output_schema.fields}
    assert field_map["value"].type == float
    assert field_map["value"].nullable is True
    assert field_map["id"].type == int


def test_rename_unknown_field_raises():
    schema = make_schema()
    with pytest.raises(RenameError, match="not found in schema"):
        Renamer(schema=schema, mapping={"nonexistent": "new_name"})


def test_rename_duplicate_target_raises():
    schema = make_schema()
    with pytest.raises(RenameError, match="Duplicate target field names"):
        Renamer(schema=schema, mapping={"id": "same", "val": "same"})


def test_repr():
    schema = make_schema()
    renamer = Renamer(schema=schema, mapping={"id": "new_id"})
    assert "Renamer" in repr(renamer)
    assert "new_id" in repr(renamer)

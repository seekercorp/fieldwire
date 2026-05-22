import pytest
from fieldwire.unpivotter import Unpivotter, UnpivotError
from fieldwire.schema import Schema, FieldSchema


def make_schema():
    return Schema(
        fields=[
            FieldSchema(name="region", type=str, nullable=False),
            FieldSchema(name="q1", type=int, nullable=False),
            FieldSchema(name="q2", type=int, nullable=False),
            FieldSchema(name="q3", type=int, nullable=False),
        ]
    )


SAMPLE_RECORDS = [
    {"region": "north", "q1": 100, "q2": 200, "q3": 150},
    {"region": "south", "q1": 80, "q2": 90, "q3": 110},
]


def test_unpivot_basic():
    u = Unpivotter(id_fields=["region"], value_fields=["q1", "q2", "q3"])
    result = u.apply(SAMPLE_RECORDS)
    assert len(result) == 6


def test_unpivot_row_structure():
    u = Unpivotter(id_fields=["region"], value_fields=["q1", "q2"])
    result = u.apply(SAMPLE_RECORDS)
    first = result[0]
    assert "region" in first
    assert "variable" in first
    assert "value" in first


def test_unpivot_custom_names():
    u = Unpivotter(
        id_fields=["region"],
        value_fields=["q1", "q2"],
        var_name="quarter",
        value_name="revenue",
    )
    result = u.apply(SAMPLE_RECORDS)
    assert "quarter" in result[0]
    assert "revenue" in result[0]


def test_unpivot_values_correct():
    u = Unpivotter(id_fields=["region"], value_fields=["q1", "q2", "q3"])
    result = u.apply(SAMPLE_RECORDS)
    north_rows = [r for r in result if r["region"] == "north"]
    by_var = {r["variable"]: r["value"] for r in north_rows}
    assert by_var["q1"] == 100
    assert by_var["q2"] == 200
    assert by_var["q3"] == 150


def test_unpivot_empty_records():
    u = Unpivotter(id_fields=["region"], value_fields=["q1"])
    assert u.apply([]) == []


def test_unpivot_missing_field_raises():
    u = Unpivotter(id_fields=["region"], value_fields=["q4"])
    with pytest.raises(UnpivotError, match="q4"):
        u.apply(SAMPLE_RECORDS, schema=make_schema())


def test_unpivot_empty_id_fields_raises():
    with pytest.raises(UnpivotError):
        Unpivotter(id_fields=[], value_fields=["q1"])


def test_unpivot_empty_value_fields_raises():
    with pytest.raises(UnpivotError):
        Unpivotter(id_fields=["region"], value_fields=[])


def test_unpivot_overlap_raises():
    with pytest.raises(UnpivotError, match="q1"):
        Unpivotter(id_fields=["region", "q1"], value_fields=["q1", "q2"])


def test_unpivot_output_schema():
    u = Unpivotter(id_fields=["region"], value_fields=["q1", "q2", "q3"])
    schema = u.output_schema(make_schema())
    names = [f.name for f in schema.fields]
    assert "region" in names
    assert "variable" in names
    assert "value" in names


def test_unpivot_repr():
    u = Unpivotter(id_fields=["region"], value_fields=["q1", "q2"])
    r = repr(u)
    assert "region" in r
    assert "q1" in r

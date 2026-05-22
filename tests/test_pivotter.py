import pytest
from fieldwire.pivotter import Pivotter, PivotError
from fieldwire.schema import Schema, FieldSchema


def make_schema():
    return Schema(
        fields=[
            FieldSchema(name="region", type=str, nullable=False),
            FieldSchema(name="product", type=str, nullable=False),
            FieldSchema(name="sales", type=int, nullable=False),
        ]
    )


SAMPLE_RECORDS = [
    {"region": "north", "product": "A", "sales": 10},
    {"region": "north", "product": "B", "sales": 20},
    {"region": "south", "product": "A", "sales": 30},
    {"region": "south", "product": "B", "sales": 40},
]


def test_pivot_basic_sum():
    p = Pivotter(index_field="region", pivot_field="product", value_field="sales")
    result = p.apply(SAMPLE_RECORDS)
    by_region = {r["region"]: r for r in result}
    assert by_region["north"]["product_A"] == 10
    assert by_region["north"]["product_B"] == 20
    assert by_region["south"]["product_A"] == 30
    assert by_region["south"]["product_B"] == 40


def test_pivot_with_schema_validates_fields():
    p = Pivotter(index_field="region", pivot_field="product", value_field="sales")
    result = p.apply(SAMPLE_RECORDS, schema=make_schema())
    assert len(result) == 2


def test_pivot_missing_field_raises():
    p = Pivotter(index_field="region", pivot_field="category", value_field="sales")
    with pytest.raises(PivotError, match="category"):
        p.apply(SAMPLE_RECORDS, schema=make_schema())


def test_pivot_same_index_and_pivot_raises():
    with pytest.raises(PivotError):
        Pivotter(index_field="region", pivot_field="region", value_field="sales")


def test_pivot_same_value_and_pivot_raises():
    with pytest.raises(PivotError):
        Pivotter(index_field="region", pivot_field="sales", value_field="sales")


def test_pivot_empty_records_returns_empty():
    p = Pivotter(index_field="region", pivot_field="product", value_field="sales")
    result = p.apply([])
    assert result == []


def test_pivot_fill_value_for_missing():
    records = [
        {"region": "north", "product": "A", "sales": 10},
        {"region": "south", "product": "B", "sales": 40},
    ]
    p = Pivotter(
        index_field="region",
        pivot_field="product",
        value_field="sales",
        fill_value=0,
    )
    result = p.apply(records)
    by_region = {r["region"]: r for r in result}
    assert by_region["north"]["product_B"] == 0
    assert by_region["south"]["product_A"] == 0


def test_pivot_custom_agg_fn():
    records = [
        {"region": "north", "product": "A", "sales": 10},
        {"region": "north", "product": "A", "sales": 20},
    ]
    p = Pivotter(
        index_field="region",
        pivot_field="product",
        value_field="sales",
        agg_fn=max,
    )
    result = p.apply(records)
    assert result[0]["product_A"] == 20


def test_pivot_output_schema():
    p = Pivotter(index_field="region", pivot_field="product", value_field="sales")
    schema = p.output_schema(SAMPLE_RECORDS)
    names = [f.name for f in schema.fields]
    assert "region" in names
    assert "product_A" in names
    assert "product_B" in names


def test_pivot_repr():
    p = Pivotter(index_field="region", pivot_field="product", value_field="sales")
    r = repr(p)
    assert "region" in r
    assert "product" in r
    assert "sales" in r


def test_pivot_preserves_index_order():
    p = Pivotter(index_field="region", pivot_field="product", value_field="sales")
    result = p.apply(SAMPLE_RECORDS)
    regions = [r["region"] for r in result]
    assert regions.index("north") < regions.index("south")

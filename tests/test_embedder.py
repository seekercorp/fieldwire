import pytest
from fieldwire.embedder import Embedder, EmbedError
from fieldwire.schema import Schema, FieldSchema


def make_schema(*extra_fields):
    base = [
        FieldSchema(name="id", type=int, nullable=False),
        FieldSchema(name="text", type=str, nullable=True),
    ]
    return Schema(fields=base + list(extra_fields))


def simple_embed(value):
    """Fake embedder: returns list of char ordinals."""
    if value is None:
        return []
    return [float(ord(c)) for c in str(value)]


# ---------------------------------------------------------------------------
# Construction / validation
# ---------------------------------------------------------------------------

def test_unknown_input_field_raises():
    schema = make_schema()
    with pytest.raises(EmbedError, match="input_field"):
        Embedder(input_field="missing", output_field="vec",
                 embed_fn=simple_embed, schema=schema)


def test_output_field_exists_raises_without_overwrite():
    schema = make_schema(FieldSchema(name="vec", type=list, nullable=True))
    with pytest.raises(EmbedError, match="already exists"):
        Embedder(input_field="text", output_field="vec",
                 embed_fn=simple_embed, schema=schema)


def test_output_field_exists_allowed_with_overwrite():
    schema = make_schema(FieldSchema(name="vec", type=list, nullable=True))
    emb = Embedder(input_field="text", output_field="vec",
                   embed_fn=simple_embed, schema=schema, overwrite=True)
    assert emb is not None


# ---------------------------------------------------------------------------
# output_schema
# ---------------------------------------------------------------------------

def test_output_schema_appends_field():
    schema = make_schema()
    emb = Embedder(input_field="text", output_field="vec",
                   embed_fn=simple_embed, schema=schema)
    out = emb.output_schema()
    names = [f.name for f in out.fields]
    assert "vec" in names


def test_output_schema_none_when_no_schema():
    emb = Embedder(input_field="text", output_field="vec", embed_fn=simple_embed)
    assert emb.output_schema() is None


# ---------------------------------------------------------------------------
# apply
# ---------------------------------------------------------------------------

def test_embed_basic_adds_vector():
    records = [{"id": 1, "text": "hi"}]
    emb = Embedder(input_field="text", output_field="vec", embed_fn=simple_embed)
    result = emb.apply(records)
    assert "vec" in result[0]
    assert isinstance(result[0]["vec"], list)


def test_embed_does_not_mutate_original():
    records = [{"id": 1, "text": "hello"}]
    emb = Embedder(input_field="text", output_field="vec", embed_fn=simple_embed)
    emb.apply(records)
    assert "vec" not in records[0]


def test_embed_multiple_records():
    records = [{"id": i, "text": str(i)} for i in range(5)]
    emb = Embedder(input_field="text", output_field="vec", embed_fn=simple_embed)
    result = emb.apply(records)
    assert len(result) == 5
    assert all("vec" in r for r in result)


def test_embed_none_value_handled_by_fn():
    records = [{"id": 1, "text": None}]
    emb = Embedder(input_field="text", output_field="vec", embed_fn=simple_embed)
    result = emb.apply(records)
    assert result[0]["vec"] == []


def test_missing_input_field_in_record_raises():
    records = [{"id": 1}]
    emb = Embedder(input_field="text", output_field="vec", embed_fn=simple_embed)
    with pytest.raises(EmbedError, match="missing input_field"):
        emb.apply(records)


def test_embed_fn_exception_raises_embed_error():
    def bad_fn(value):
        raise ValueError("boom")

    records = [{"id": 1, "text": "hello"}]
    emb = Embedder(input_field="text", output_field="vec", embed_fn=bad_fn)
    with pytest.raises(EmbedError, match="boom"):
        emb.apply(records)


def test_embed_fn_non_list_return_raises():
    emb = Embedder(input_field="text", output_field="vec",
                   embed_fn=lambda v: "not-a-list")
    with pytest.raises(EmbedError, match="must return a list"):
        emb.apply([{"id": 1, "text": "hi"}])


def test_embed_empty_records_returns_empty():
    emb = Embedder(input_field="text", output_field="vec", embed_fn=simple_embed)
    assert emb.apply([]) == []


def test_repr_contains_field_names():
    emb = Embedder(input_field="text", output_field="vec", embed_fn=simple_embed)
    r = repr(emb)
    assert "text" in r
    assert "vec" in r

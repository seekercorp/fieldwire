"""Tests for the Pipeline and Step classes."""

import pytest
from fieldwire.pipeline import Pipeline, PipelineError, Step
from fieldwire.schema import FieldSchema, Schema


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

INPUT_SCHEMA = Schema(
    fields=[
        FieldSchema(name="id", type=int, nullable=False),
        FieldSchema(name="value", type=float, nullable=False),
    ]
)

OUTPUT_SCHEMA = Schema(
    fields=[
        FieldSchema(name="id", type=int, nullable=False),
        FieldSchema(name="value", type=float, nullable=False),
        FieldSchema(name="label", type=str, nullable=False),
    ]
)


def add_label(record):
    return {**record, "label": f"item-{record['id']}"}


def double_value(record):
    return {**record, "value": record["value"] * 2}


# ---------------------------------------------------------------------------
# Step tests
# ---------------------------------------------------------------------------

class TestStep:
    def test_run_no_schemas(self):
        step = Step("double", double_value)
        result = step.run({"id": 1, "value": 3.0})
        assert result["value"] == 6.0

    def test_run_with_valid_input_schema(self):
        step = Step("double", double_value, input_schema=INPUT_SCHEMA)
        result = step.run({"id": 1, "value": 2.5})
        assert result["value"] == 5.0

    def test_run_invalid_input_raises(self):
        step = Step("double", double_value, input_schema=INPUT_SCHEMA)
        with pytest.raises(PipelineError, match="input validation failed"):
            step.run({"id": "bad", "value": 2.5})

    def test_run_invalid_output_raises(self):
        step = Step("add_label", add_label, output_schema=INPUT_SCHEMA)
        # OUTPUT has extra 'label' field not in INPUT_SCHEMA — schema allows
        # extra keys, but 'label' being str is fine; let's break output type.
        def bad_transform(r):
            return {**r, "id": "not-an-int"}

        step2 = Step("bad", bad_transform, output_schema=INPUT_SCHEMA)
        with pytest.raises(PipelineError, match="output validation failed"):
            step2.run({"id": 1, "value": 1.0})


# ---------------------------------------------------------------------------
# Pipeline tests
# ---------------------------------------------------------------------------

class TestPipeline:
    def test_add_step_returns_self(self):
        p = Pipeline()
        step = Step("s", lambda r: r)
        assert p.add_step(step) is p

    def test_steps_property(self):
        p = Pipeline()
        s1 = Step("s1", lambda r: r)
        s2 = Step("s2", lambda r: r)
        p.add_step(s1).add_step(s2)
        assert p.steps == [s1, s2]

    def test_run_one_chains_steps(self):
        p = Pipeline()
        p.add_step(Step("double", double_value))
        p.add_step(Step("label", add_label))
        result = p.run_one({"id": 3, "value": 4.0})
        assert result["value"] == 8.0
        assert result["label"] == "item-3"

    def test_run_processes_multiple_records(self):
        p = Pipeline().add_step(Step("double", double_value))
        records = [{"id": i, "value": float(i)} for i in range(3)]
        results = p.run(records)
        assert [r["value"] for r in results] == [0.0, 2.0, 4.0]

    def test_run_one_propagates_pipeline_error(self):
        p = Pipeline().add_step(
            Step("double", double_value, input_schema=INPUT_SCHEMA)
        )
        with pytest.raises(PipelineError):
            p.run_one({"id": None, "value": 1.0})

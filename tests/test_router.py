import pytest
from fieldwire.router import Router, RouterError


RECORDS = [
    {"id": 1, "score": 90, "label": "A"},
    {"id": 2, "score": 55, "label": "B"},
    {"id": 3, "score": 72, "label": "A"},
    {"id": 4, "score": 40, "label": "C"},
    {"id": 5, "score": 85, "label": "B"},
]


def test_router_basic_routing():
    r = Router(rules=[
        ("high", lambda rec: rec["score"] >= 80),
        ("mid",  lambda rec: rec["score"] >= 60),
        ("low",  lambda rec: True),
    ])
    result = r.route(RECORDS)
    assert {rec["id"] for rec in result["high"]} == {1, 5}
    assert {rec["id"] for rec in result["mid"]}  == {3}
    assert {rec["id"] for rec in result["low"]}  == {2, 4}


def test_router_first_match_wins():
    r = Router(rules=[
        ("always", lambda rec: True),
        ("never",  lambda rec: True),
    ])
    result = r.route(RECORDS)
    assert len(result["always"]) == len(RECORDS)
    assert result.get("never", []) == []


def test_router_unmatched_goes_to_default():
    r = Router(
        rules=[("high", lambda rec: rec["score"] >= 80)],
        default_route="other",
    )
    result = r.route(RECORDS)
    assert {rec["id"] for rec in result["high"]}  == {1, 5}
    assert {rec["id"] for rec in result["other"]} == {2, 3, 4}


def test_router_unmatched_dropped_without_default():
    r = Router(rules=[("high", lambda rec: rec["score"] >= 80)])
    result = r.route(RECORDS)
    assert len(result.get("high", [])) == 2
    assert "other" not in result


def test_router_does_not_mutate_original():
    records = [{"id": 1, "score": 90, "label": "A"}]
    r = Router(rules=[("high", lambda rec: True)])
    result = r.route(records)
    result["high"][0]["score"] = 0
    assert records[0]["score"] == 90


def test_router_empty_records():
    r = Router(rules=[("high", lambda rec: rec["score"] >= 80)])
    result = r.route([])
    assert result.get("high", []) == []


def test_router_no_rules_raises():
    with pytest.raises(RouterError, match="At least one rule"):
        Router(rules=[])


def test_router_duplicate_route_name_raises():
    with pytest.raises(RouterError, match="Duplicate route name"):
        Router(rules=[
            ("dup", lambda r: True),
            ("dup", lambda r: False),
        ])


def test_router_non_callable_predicate_raises():
    with pytest.raises(RouterError, match="callable"):
        Router(rules=[("bad", "not_a_fn")])  # type: ignore


def test_router_predicate_exception_raises():
    def boom(rec):
        raise ValueError("explode")

    r = Router(rules=[("x", boom)])
    with pytest.raises(RouterError, match="raised"):
        r.route(RECORDS)


def test_router_route_names():
    r = Router(
        rules=[("a", lambda rec: True), ("b", lambda rec: False)],
        default_route="fallback",
    )
    assert r.route_names() == ["a", "b", "fallback"]


def test_router_repr():
    r = Router(rules=[("hi", lambda rec: True)], default_route="lo")
    assert "hi" in repr(r)
    assert "lo" in repr(r)

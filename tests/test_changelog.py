import pytest
from fieldwire.changelog import Changelog, ChangelogEntry, ChangelogError


V1 = [
    {"id": 1, "value": 100},
    {"id": 2, "value": 200},
]

V2 = [
    {"id": 1, "value": 150},  # changed
    {"id": 2, "value": 200},  # unchanged
    {"id": 3, "value": 300},  # added
]

V3 = [
    {"id": 2, "value": 200},  # unchanged
    {"id": 3, "value": 300},  # unchanged
    # id=1 removed
]


def test_first_commit_all_added():
    cl = Changelog(key="id")
    entry = cl.commit(V1)
    assert entry.version == 1
    assert len(entry.added) == 2
    assert entry.removed == []
    assert entry.changed == []


def test_second_commit_detects_changes():
    cl = Changelog(key="id")
    cl.commit(V1)
    entry = cl.commit(V2)
    assert entry.version == 2
    assert len(entry.added) == 1
    assert entry.added[0]["id"] == 3
    assert len(entry.changed) == 1
    assert entry.changed[0]["before"]["value"] == 100
    assert entry.changed[0]["after"]["value"] == 150
    assert entry.removed == []


def test_third_commit_detects_removal():
    cl = Changelog(key="id")
    cl.commit(V1)
    cl.commit(V2)
    entry = cl.commit(V3)
    assert entry.version == 3
    assert len(entry.removed) == 1
    assert entry.removed[0]["id"] == 1


def test_history_length():
    cl = Changelog(key="id")
    cl.commit(V1)
    cl.commit(V2)
    cl.commit(V3)
    assert len(cl.history()) == 3


def test_latest_returns_last_entry():
    cl = Changelog(key="id")
    cl.commit(V1)
    e2 = cl.commit(V2)
    assert cl.latest() is e2


def test_latest_on_empty_returns_none():
    cl = Changelog(key="id")
    assert cl.latest() is None


def test_summary_structure():
    cl = Changelog(key="id")
    cl.commit(V1)
    cl.commit(V2)
    summary = cl.summary()
    assert len(summary) == 2
    assert summary[0]["version"] == 1
    assert "added" in summary[0]
    assert "removed" in summary[0]
    assert "changed" in summary[0]
    assert "total_changes" in summary[0]


def test_total_changes_counts_all():
    cl = Changelog(key="id")
    cl.commit(V1)
    entry = cl.commit(V2)
    # 1 changed + 1 added = 2
    assert entry.total_changes == 2


def test_compare_fields_limits_change_detection():
    cl = Changelog(key="id", compare_fields=["value"])
    before = [{"id": 1, "value": 10, "label": "a"}]
    after = [{"id": 1, "value": 10, "label": "b"}]  # label changed, value same
    cl.commit(before)
    entry = cl.commit(after)
    assert entry.changed == []


def test_changelog_repr():
    cl = Changelog(key="id")
    cl.commit(V1)
    r = repr(cl)
    assert "id" in r
    assert "versions=1" in r


def test_commit_same_data_no_changes():
    cl = Changelog(key="id")
    cl.commit(V1)
    entry = cl.commit(V1)
    assert entry.total_changes == 0
    assert len(entry.added) == 0
    assert len(entry.removed) == 0
    assert len(entry.changed) == 0

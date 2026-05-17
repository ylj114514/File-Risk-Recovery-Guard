from file_guard.detector import detect_bulk_change, detect_changes
from file_guard.models import FileSnapshot


def snapshot(path: str, sha: str) -> FileSnapshot:
    return FileSnapshot(
        relative_path=path,
        absolute_path=f"/demo/{path}",
        file_name=path,
        extension=".txt",
        size=10,
        mtime=1.0,
        sha256=sha,
        sensitivity="HIGH" if "account" in path else "LOW",
    )


def test_created_detected():
    changes = detect_changes({}, {"new.txt": snapshot("new.txt", "a")})
    assert changes[0]["event_type"] == "CREATED"


def test_deleted_detected():
    changes = detect_changes({"old.txt": snapshot("old.txt", "a")}, {})
    assert changes[0]["event_type"] == "DELETED"


def test_modified_detected():
    changes = detect_changes({"a.txt": snapshot("a.txt", "a")}, {"a.txt": snapshot("a.txt", "b")})
    assert changes[0]["event_type"] == "MODIFIED"


def test_detect_bulk_change():
    changes = [
        {"event_type": "MODIFIED"},
        {"event_type": "DELETED"},
        {"event_type": "CREATED"},
    ]
    assert detect_bulk_change(changes) is True

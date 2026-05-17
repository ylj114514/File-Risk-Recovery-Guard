"""Change detection between baseline and current file snapshots."""

from __future__ import annotations

from .config import SUSPICIOUS_EXTENSIONS
from .models import FileSnapshot


def _snapshot_to_change_fields(snapshot: FileSnapshot | None) -> dict:
    """Extract common snapshot fields for detector output."""
    if snapshot is None:
        return {
            "hash": None,
            "size": None,
            "sensitivity": "LOW",
            "extension": "",
            "file_name": "",
        }
    return {
        "hash": snapshot.sha256,
        "size": snapshot.size,
        "sensitivity": snapshot.sensitivity,
        "extension": snapshot.extension,
        "file_name": snapshot.file_name,
    }


def _make_change(
    event_type: str,
    relative_path: str,
    old_snapshot: FileSnapshot | None,
    new_snapshot: FileSnapshot | None,
) -> dict:
    """Build a raw detector change dictionary."""
    old_fields = _snapshot_to_change_fields(old_snapshot)
    new_fields = _snapshot_to_change_fields(new_snapshot)
    effective = new_snapshot or old_snapshot
    return {
        "event_type": event_type,
        "relative_path": relative_path,
        "old_snapshot": old_snapshot,
        "new_snapshot": new_snapshot,
        "old_hash": old_fields["hash"],
        "new_hash": new_fields["hash"],
        "old_size": old_fields["size"],
        "new_size": new_fields["size"],
        "sensitivity": effective.sensitivity if effective else "LOW",
        "extension": (effective.extension if effective else "").lower(),
        "file_name": effective.file_name if effective else "",
    }


def detect_changes(
    baseline: dict[str, FileSnapshot],
    current: dict[str, FileSnapshot]
) -> list[dict]:
    """
    对比基线快照和当前快照，生成原始变更事件。
    """
    changes: list[dict] = []
    all_paths = sorted(set(baseline) | set(current))
    for relative_path in all_paths:
        old_snapshot = baseline.get(relative_path)
        new_snapshot = current.get(relative_path)
        if old_snapshot is None and new_snapshot is not None:
            changes.append(_make_change("CREATED", relative_path, None, new_snapshot))
        elif old_snapshot is not None and new_snapshot is None:
            changes.append(_make_change("DELETED", relative_path, old_snapshot, None))
        elif old_snapshot and new_snapshot and old_snapshot.sha256 != new_snapshot.sha256:
            changes.append(_make_change("MODIFIED", relative_path, old_snapshot, new_snapshot))
    return changes


def detect_bulk_change(changes: list[dict], threshold: int = 3) -> bool:
    """
    判断是否发生批量变更。
    """
    base_events = {"CREATED", "MODIFIED", "DELETED"}
    return sum(1 for change in changes if change.get("event_type") in base_events) >= threshold


def enrich_special_events(changes: list[dict], is_bulk: bool) -> list[dict]:
    """
    根据原始变化补充特殊事件标记，例如高敏感文件变化、可疑扩展名、批量变更。
    """
    enriched = list(changes)
    for change in changes:
        event_type = change.get("event_type")
        extension = str(change.get("extension", "")).lower()
        sensitivity = change.get("sensitivity")
        if event_type == "CREATED" and extension in SUSPICIOUS_EXTENSIONS:
            special = dict(change)
            special["event_type"] = "SUSPICIOUS_EXTENSION"
            enriched.append(special)
        if event_type in {"DELETED", "MODIFIED"} and sensitivity == "HIGH":
            special = dict(change)
            special["event_type"] = "HIGH_SENSITIVE_CHANGED"
            enriched.append(special)

    if is_bulk:
        affected_paths = [change["relative_path"] for change in changes]
        enriched.append(
            {
                "event_type": "BULK_CHANGE",
                "relative_path": ", ".join(affected_paths),
                "old_snapshot": None,
                "new_snapshot": None,
                "old_hash": None,
                "new_hash": None,
                "old_size": None,
                "new_size": None,
                "sensitivity": "HIGH" if any(c.get("sensitivity") == "HIGH" for c in changes) else "MEDIUM",
                "extension": "",
                "file_name": "multiple files",
                "change_count": len(changes),
                "affected_paths": affected_paths,
            }
        )
    return enriched

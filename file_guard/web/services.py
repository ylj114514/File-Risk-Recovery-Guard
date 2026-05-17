"""Service layer used by Flask routes and tests."""

from __future__ import annotations

import shutil
from pathlib import Path

from ..backup import backup_files, restore_file, verify_restored_file
from ..baseline import get_baseline_count, init_database, load_baseline, save_baseline
from ..config import BACKUP_DIR, DB_PATH, DEMO_WORKSPACE_DIR, OUTPUT_DIR, PROTECTED_DIR
from ..demo import (
    create_demo_workspace,
    reset_demo_workspace,
    simulate_bulk_change,
    simulate_delete,
    simulate_modify,
    simulate_suspicious_file,
)
from ..detector import detect_bulk_change, detect_changes, enrich_special_events
from ..reporter import export_events_csv, export_events_json, generate_html_report, load_events_from_db, save_events_to_db
from ..risk_engine import build_risk_event
from ..scanner import scan_directory
from ..utils import ensure_dir, human_size, is_safe_relative_path


def _response(success: bool, message: str, data: dict | None = None) -> dict:
    """Return the API response shape used by mutating services."""
    return {"success": success, "message": message, "data": data if data is not None else {}}


def _level_distribution(events: list) -> dict[str, int]:
    counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for event in events:
        counts[event.level] = counts.get(event.level, 0) + 1
    return counts


def get_system_status() -> dict:
    """
    返回系统状态统计。
    """
    init_database(DB_PATH)
    baseline_count = get_baseline_count(DB_PATH)
    events = load_events_from_db(DB_PATH)
    distribution = _level_distribution(events)
    latest_events = [event.to_dict() for event in events[:5]]
    return {
        "protected_file_count": baseline_count,
        "risk_event_count": len(events),
        "high_event_count": distribution.get("HIGH", 0),
        "critical_event_count": distribution.get("CRITICAL", 0),
        "latest_event_time": events[0].detected_at if events else "暂无",
        "level_distribution": distribution,
        "latest_events": latest_events,
    }


def get_baseline_files() -> list[dict]:
    """
    返回基线文件列表。
    """
    baseline = load_baseline(DB_PATH)
    files = []
    for snapshot in baseline.values():
        item = snapshot.to_dict()
        item["size_text"] = human_size(snapshot.size)
        item["hash_short"] = snapshot.sha256[:16]
        files.append(item)
    return files


def get_risk_events() -> list[dict]:
    """
    返回风险事件列表。
    """
    return [event.to_dict() for event in load_events_from_db(DB_PATH)]


def run_demo_init() -> dict:
    """
    创建演示环境。
    """
    try:
        root = create_demo_workspace(DEMO_WORKSPACE_DIR)
        return _response(True, "演示环境创建成功。", {"root": str(root), "file_count": len(list(root.glob('*')))})
    except Exception as exc:
        return _response(False, f"演示环境创建失败：{exc}", None)


def run_baseline_init() -> dict:
    """
    初始化基线。
    """
    try:
        init_database(DB_PATH)
        snapshots = scan_directory(PROTECTED_DIR)
        save_baseline(DB_PATH, snapshots)
        backup_files(PROTECTED_DIR, BACKUP_DIR, snapshots, DB_PATH)
        return _response(
            True,
            "基线初始化成功。",
            {"scanned_files": len(snapshots), "backup_files": len(snapshots), "database": str(DB_PATH)},
        )
    except Exception as exc:
        return _response(False, f"基线初始化失败：{exc}", None)


def run_scan() -> dict:
    """
    执行扫描检测。
    """
    try:
        init_database(DB_PATH)
        baseline = load_baseline(DB_PATH)
        current = scan_directory(PROTECTED_DIR)
        changes = detect_changes(baseline, current)
        is_bulk = detect_bulk_change(changes)
        enriched = enrich_special_events(changes, is_bulk)
        events = [build_risk_event(change, is_bulk=is_bulk) for change in enriched]
        save_events_to_db(DB_PATH, events)
        distribution = _level_distribution(events)
        return _response(
            True,
            f"扫描完成，发现 {len(events)} 条风险事件。",
            {
                "event_count": len(events),
                "is_bulk_change": is_bulk,
                "has_high_sensitive_change": any(e.event_type == "HIGH_SENSITIVE_CHANGED" for e in events),
                "level_distribution": distribution,
                "events": [event.to_dict() for event in events],
            },
        )
    except Exception as exc:
        return _response(False, f"扫描失败：{exc}", None)


def run_simulation(case: str) -> dict:
    """
    执行安全模拟。
    """
    try:
        if case == "modify":
            simulate_modify(PROTECTED_DIR)
            message = "已模拟篡改 finance_report.txt。"
        elif case == "delete":
            simulate_delete(PROTECTED_DIR)
            message = "已模拟删除 account_list.txt。"
        elif case == "bulk":
            simulate_bulk_change(PROTECTED_DIR)
            message = "已模拟批量变更 3 个文件。"
        elif case == "suspicious":
            simulate_suspicious_file(PROTECTED_DIR)
            message = "已模拟新增 suspicious.ps1，无害文本，未执行。"
        else:
            return _response(False, "不支持的模拟类型。", None)
        return _response(True, message, {"case": case})
    except Exception as exc:
        return _response(False, f"模拟失败：{exc}", None)


def run_restore(relative_path: str) -> dict:
    """
    恢复指定文件。
    """
    if not is_safe_relative_path(relative_path):
        return _response(False, "非法路径，禁止 ../、绝对路径和路径穿越。", None)
    try:
        baseline = load_baseline(DB_PATH)
        restored = restore_file(PROTECTED_DIR, BACKUP_DIR, relative_path)
        if not restored:
            return _response(False, "备份文件不存在，无法恢复。", {"path": relative_path})
        verified, verify_message = verify_restored_file(PROTECTED_DIR, baseline, relative_path)
        if not verified:
            return _response(False, f"文件已复制但校验失败：{verify_message}", {"path": relative_path})
        return _response(
            True,
            f"{relative_path} 恢复成功，哈希校验通过。",
            {"path": relative_path, "verified": True, "verification": verify_message},
        )
    except Exception as exc:
        return _response(False, f"恢复失败：{exc}", None)


def run_report_export() -> dict:
    """
    导出 JSON、CSV、HTML 报告。
    """
    try:
        events = load_events_from_db(DB_PATH)
        ensure_dir(OUTPUT_DIR)
        json_path = OUTPUT_DIR / "events.json"
        csv_path = OUTPUT_DIR / "events.csv"
        html_path = OUTPUT_DIR / "report.html"
        export_events_json(events, json_path)
        export_events_csv(events, csv_path)
        generate_html_report(events, html_path, PROTECTED_DIR)
        return _response(
            True,
            "报告导出成功。",
            {
                "json": str(json_path),
                "csv": str(csv_path),
                "html": str(html_path),
                "event_count": len(events),
            },
        )
    except Exception as exc:
        return _response(False, f"报告导出失败：{exc}", None)


def run_reset() -> dict:
    """
    重置演示环境。
    """
    try:
        reset_demo_workspace(DEMO_WORKSPACE_DIR)
        if DB_PATH.exists():
            DB_PATH.unlink()
        if BACKUP_DIR.exists():
            shutil.rmtree(BACKUP_DIR)
        ensure_dir(BACKUP_DIR)
        ensure_dir(OUTPUT_DIR)
        for file_path in OUTPUT_DIR.glob("*"):
            if file_path.is_file():
                try:
                    file_path.unlink()
                except PermissionError:
                    pass
        return _response(True, "演示环境、数据库、备份和输出文件已重置。", {"root": str(PROTECTED_DIR)})
    except Exception as exc:
        return _response(False, f"重置失败：{exc}", None)

"""Command line interface for File-Risk-Recovery-Guard."""

from __future__ import annotations

import argparse
import logging
import shutil
from pathlib import Path

from .backup import backup_files, restore_file, verify_restored_file
from .baseline import get_baseline_count, init_database, load_baseline, save_baseline
from .config import BACKUP_DIR, DB_PATH, DEFAULT_HOST, DEFAULT_PORT, DEMO_WORKSPACE_DIR, OUTPUT_DIR, PROTECTED_DIR
from .demo import (
    create_demo_workspace,
    reset_demo_workspace,
    simulate_bulk_change,
    simulate_delete,
    simulate_modify,
    simulate_suspicious_file,
)
from .detector import detect_bulk_change, detect_changes, enrich_special_events
from .reporter import export_events_csv, export_events_json, generate_html_report, load_events_from_db, save_events_to_db
from .risk_engine import build_risk_event
from .scanner import scan_directory
from .utils import ensure_dir, ensure_inside_demo_workspace, setup_logging


def _resolve_root(root: str | None) -> Path:
    """Resolve and validate the protected root directory argument."""
    path = Path(root) if root else PROTECTED_DIR
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve(strict=False)
    ensure_inside_demo_workspace(path)
    if path != PROTECTED_DIR.resolve(strict=False):
        raise ValueError("root must be demo_workspace/protected_files")
    return path


def _init_command(args: argparse.Namespace) -> None:
    root = _resolve_root(args.root)
    init_database(DB_PATH)
    snapshots = scan_directory(root)
    save_baseline(DB_PATH, snapshots)
    backup_files(root, BACKUP_DIR, snapshots, DB_PATH)
    print("[OK] Baseline initialized.")
    print(f"Scanned files: {len(snapshots)}")
    print(f"Backup files: {len(snapshots)}")
    print(f"Database: {DB_PATH.relative_to(Path.cwd()) if DB_PATH.is_relative_to(Path.cwd()) else DB_PATH}")


def _scan_command(args: argparse.Namespace) -> None:
    root = _resolve_root(args.root)
    init_database(DB_PATH)
    baseline = load_baseline(DB_PATH)
    current = scan_directory(root)
    changes = detect_changes(baseline, current)
    is_bulk = detect_bulk_change(changes)
    enriched = enrich_special_events(changes, is_bulk)
    events = [build_risk_event(change, is_bulk=is_bulk) for change in enriched]
    save_events_to_db(DB_PATH, events)
    print(f"Risk events detected: {len(events)}")
    for event in events:
        print()
        print(f"[{event.level}] {event.event_type} {event.relative_path}")
        print(f"Score: {event.score}")
        print(f"Evidence: {event.evidence}")
        print(f"Suggestion: {event.suggestion}")


def _simulate_command(args: argparse.Namespace) -> None:
    root = PROTECTED_DIR
    ensure_inside_demo_workspace(root)
    if args.case == "modify":
        simulate_modify(root)
        print("[SIMULATE] Modified sensitive file: finance_report.txt")
    elif args.case == "delete":
        simulate_delete(root)
        print("[SIMULATE] Deleted sensitive file: account_list.txt")
    elif args.case == "bulk":
        simulate_bulk_change(root)
        print("[SIMULATE] Bulk changed files: finance_report.txt, contract_2025.txt, project_plan.txt")
    elif args.case == "suspicious":
        simulate_suspicious_file(root)
        print("[SIMULATE] Created harmless suspicious extension file: suspicious.ps1")
    else:
        raise ValueError(f"Unsupported simulation case: {args.case}")


def _restore_command(args: argparse.Namespace) -> None:
    baseline = load_baseline(DB_PATH)
    restored = restore_file(PROTECTED_DIR, BACKUP_DIR, args.path)
    if restored:
        print(f"[OK] Restored {args.path} from backup.")
    else:
        print(f"[FAIL] Backup file not found for {args.path}.")
        return
    verified, message = verify_restored_file(PROTECTED_DIR, baseline, args.path)
    if verified:
        print("[OK] Hash verification passed.")
    else:
        print(f"[FAIL] {message}")


def _report_command(_: argparse.Namespace) -> None:
    events = load_events_from_db(DB_PATH)
    json_path = OUTPUT_DIR / "events.json"
    csv_path = OUTPUT_DIR / "events.csv"
    html_path = OUTPUT_DIR / "report.html"
    export_events_json(events, json_path)
    export_events_csv(events, csv_path)
    generate_html_report(events, html_path, PROTECTED_DIR)
    print(f"[OK] JSON exported: {json_path}")
    print(f"[OK] CSV exported: {csv_path}")
    print(f"[OK] HTML report generated: {html_path}")


def _reset_command(_: argparse.Namespace) -> None:
    reset_demo_workspace(DEMO_WORKSPACE_DIR)
    if DB_PATH.exists():
        DB_PATH.unlink()
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    ensure_dir(BACKUP_DIR)
    ensure_dir(OUTPUT_DIR)
    logging.shutdown()
    for file_path in OUTPUT_DIR.glob("*"):
        if file_path.is_file():
            file_path.unlink()
    print("[OK] Demo workspace, database, backups, and outputs reset.")
    print(f"[OK] Protected files regenerated: {PROTECTED_DIR}")


def build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser."""
    parser = argparse.ArgumentParser(prog="file-risk-recovery-guard")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("demo-init", help="create demo workspace").set_defaults(
        func=lambda _: (
            create_demo_workspace(DEMO_WORKSPACE_DIR),
            print(f"[OK] Demo workspace created: {PROTECTED_DIR}"),
            print("[OK] Protected files generated."),
        )
    )

    init_parser = subparsers.add_parser("init", help="initialize baseline and backups")
    init_parser.add_argument("--root", default=str(PROTECTED_DIR))
    init_parser.set_defaults(func=_init_command)

    scan_parser = subparsers.add_parser("scan", help="scan and detect risks")
    scan_parser.add_argument("--root", default=str(PROTECTED_DIR))
    scan_parser.set_defaults(func=_scan_command)

    simulate_parser = subparsers.add_parser("simulate", help="run a safe demo risk simulation")
    simulate_parser.add_argument("--case", choices=["modify", "delete", "bulk", "suspicious"], required=True)
    simulate_parser.set_defaults(func=_simulate_command)

    restore_parser = subparsers.add_parser("restore", help="restore a file from backup")
    restore_parser.add_argument("--path", required=True)
    restore_parser.set_defaults(func=_restore_command)

    subparsers.add_parser("report", help="export JSON, CSV, and HTML report").set_defaults(func=_report_command)

    web_parser = subparsers.add_parser("web", help="start local web console")
    web_parser.add_argument("--host", default=DEFAULT_HOST)
    web_parser.add_argument("--port", default=DEFAULT_PORT, type=int)
    web_parser.set_defaults(func=_web_command)

    subparsers.add_parser("reset", help="reset demo workspace and outputs").set_defaults(func=_reset_command)
    return parser


def _web_command(args: argparse.Namespace) -> None:
    from .web.app import create_app

    app = create_app()
    print("[OK] File-Risk-Recovery-Guard Web Console started.")
    print(f"URL: http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port)


def main() -> None:
    """CLI entry point."""
    setup_logging()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

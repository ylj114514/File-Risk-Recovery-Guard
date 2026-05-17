"""SQLite database and baseline persistence functions."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import FileSnapshot
from .utils import ensure_dir, now_text


def init_database(db_path: Path) -> None:
    """
    初始化 SQLite 数据库表结构。
    """
    ensure_dir(db_path.parent)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS baseline_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                relative_path TEXT UNIQUE NOT NULL,
                absolute_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                extension TEXT,
                size INTEGER NOT NULL,
                mtime REAL NOT NULL,
                sha256 TEXT NOT NULL,
                sensitivity TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS risk_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                relative_path TEXT NOT NULL,
                old_hash TEXT,
                new_hash TEXT,
                old_size INTEGER,
                new_size INTEGER,
                score INTEGER NOT NULL,
                level TEXT NOT NULL,
                evidence TEXT NOT NULL,
                suggestion TEXT NOT NULL,
                detected_at TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                relative_path TEXT UNIQUE NOT NULL,
                backup_path TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.commit()


def save_baseline(db_path: Path, snapshots: dict[str, FileSnapshot]) -> None:
    """
    清空旧基线，保存新的文件基线。
    """
    init_database(db_path)
    created_at = now_text()
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM baseline_files")
        conn.executemany(
            """
            INSERT INTO baseline_files (
                relative_path, absolute_path, file_name, extension, size,
                mtime, sha256, sensitivity, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    snapshot.relative_path,
                    snapshot.absolute_path,
                    snapshot.file_name,
                    snapshot.extension,
                    snapshot.size,
                    snapshot.mtime,
                    snapshot.sha256,
                    snapshot.sensitivity,
                    created_at,
                )
                for snapshot in snapshots.values()
            ],
        )
        conn.commit()


def load_baseline(db_path: Path) -> dict[str, FileSnapshot]:
    """
    从数据库读取历史文件基线。
    """
    if not db_path.exists():
        return {}
    init_database(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT relative_path, absolute_path, file_name, extension,
                   size, mtime, sha256, sensitivity
            FROM baseline_files
            ORDER BY relative_path
            """
        ).fetchall()
    return {
        row["relative_path"]: FileSnapshot(
            relative_path=row["relative_path"],
            absolute_path=row["absolute_path"],
            file_name=row["file_name"],
            extension=row["extension"] or "",
            size=int(row["size"]),
            mtime=float(row["mtime"]),
            sha256=row["sha256"],
            sensitivity=row["sensitivity"],
        )
        for row in rows
    }


def get_baseline_count(db_path: Path) -> int:
    """
    返回基线文件数量。
    """
    if not db_path.exists():
        return 0
    init_database(db_path)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) FROM baseline_files").fetchone()
    return int(row[0])

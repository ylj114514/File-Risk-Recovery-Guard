"""Backup, restore, and hash verification functions."""

from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

from .baseline import init_database
from .models import FileSnapshot
from .scanner import calculate_sha256
from .utils import ensure_dir, ensure_inside_demo_workspace, ensure_inside_project, is_safe_relative_path, now_text


def backup_files(
    root_dir: Path,
    backup_dir: Path,
    snapshots: dict[str, FileSnapshot],
    db_path: Path
) -> None:
    """
    将基线文件复制到备份目录，并记录备份信息。
    """
    root_dir = ensure_inside_demo_workspace(root_dir)
    backup_dir = ensure_inside_project(backup_dir)
    ensure_dir(backup_dir)
    init_database(db_path)
    created_at = now_text()

    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM backups")
        for relative_path, snapshot in snapshots.items():
            if not is_safe_relative_path(relative_path):
                raise ValueError(f"Unsafe relative path in snapshot: {relative_path}")
            source = (root_dir / relative_path).resolve(strict=False)
            source.relative_to(root_dir)
            target = (backup_dir / relative_path).resolve(strict=False)
            target.relative_to(backup_dir)
            ensure_dir(target.parent)
            shutil.copy2(source, target)
            conn.execute(
                """
                INSERT OR REPLACE INTO backups
                    (relative_path, backup_path, sha256, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (relative_path, str(target), snapshot.sha256, created_at),
            )
        conn.commit()


def restore_file(
    root_dir: Path,
    backup_dir: Path,
    relative_path: str
) -> bool:
    """
    从备份目录恢复指定文件。
    """
    if not is_safe_relative_path(relative_path):
        raise ValueError("Unsafe relative path. '../' and absolute paths are forbidden.")
    root_dir = ensure_inside_demo_workspace(root_dir)
    backup_dir = ensure_inside_project(backup_dir)
    source = (backup_dir / relative_path).resolve(strict=False)
    target = (root_dir / relative_path).resolve(strict=False)
    source.relative_to(backup_dir)
    target.relative_to(root_dir)
    if not source.exists() or not source.is_file():
        return False
    ensure_dir(target.parent)
    shutil.copy2(source, target)
    return True


def verify_restored_file(
    root_dir: Path,
    baseline: dict[str, FileSnapshot],
    relative_path: str
) -> tuple[bool, str]:
    """
    恢复后重新计算文件哈希，并与基线哈希对比。
    返回是否验证成功和说明文本。
    """
    if not is_safe_relative_path(relative_path):
        return False, "非法路径，禁止路径穿越或绝对路径。"
    root_dir = ensure_inside_demo_workspace(root_dir)
    expected = baseline.get(relative_path)
    if expected is None:
        return False, "基线中不存在该文件，无法验证。"
    target = (root_dir / relative_path).resolve(strict=False)
    try:
        target.relative_to(root_dir)
    except ValueError:
        return False, "目标路径超出演示目录。"
    if not target.exists():
        return False, "恢复目标文件不存在。"
    actual_hash = calculate_sha256(target)
    if actual_hash == expected.sha256:
        return True, "Hash verification passed."
    return False, f"Hash verification failed. expected={expected.sha256}, actual={actual_hash}"

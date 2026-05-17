"""Shared utility functions and path safety helpers."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path, PurePath

from .config import DEMO_WORKSPACE_DIR, LOG_PATH, OUTPUT_DIR, PROJECT_ROOT


def ensure_dir(path: Path) -> None:
    """
    确保目录存在。
    """
    path.mkdir(parents=True, exist_ok=True)


def now_text() -> str:
    """
    返回当前时间字符串。
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def is_safe_relative_path(relative_path: str) -> bool:
    """
    判断相对路径是否安全，禁止 ../ 和绝对路径。
    """
    if not relative_path or "\x00" in relative_path:
        return False
    raw = relative_path.replace("\\", "/")
    if raw.startswith("/") or raw.startswith("//"):
        return False
    path = PurePath(relative_path)
    if path.is_absolute():
        return False
    return ".." not in path.parts


def _is_inside(path: Path, parent: Path) -> bool:
    resolved_path = path.resolve(strict=False)
    resolved_parent = parent.resolve(strict=False)
    try:
        resolved_path.relative_to(resolved_parent)
        return True
    except ValueError:
        return False


def ensure_inside_project(path: Path) -> Path:
    """
    确保路径位于项目目录内。
    """
    resolved = path.resolve(strict=False)
    if not _is_inside(resolved, PROJECT_ROOT):
        raise ValueError(f"Path is outside project directory: {path}")
    return resolved


def ensure_inside_demo_workspace(path: Path) -> Path:
    """
    确保路径位于 demo_workspace 内。
    """
    resolved = path.resolve(strict=False)
    if not _is_inside(resolved, DEMO_WORKSPACE_DIR):
        raise ValueError(f"Path is outside demo workspace: {path}")
    return resolved


def setup_logging() -> None:
    """
    初始化日志。
    """
    ensure_dir(OUTPUT_DIR)
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        force=True,
    )


def human_size(size: int) -> str:
    """
    将文件大小转换为可读字符串。
    """
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size} B"

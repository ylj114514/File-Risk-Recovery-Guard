"""Directory scanner and file hash calculation."""

from __future__ import annotations

import hashlib
from pathlib import Path

from .config import MEDIUM_KEYWORDS, PROTECTED_DIR, SENSITIVE_KEYWORDS
from .models import FileSnapshot
from .utils import ensure_inside_demo_workspace


def calculate_sha256(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    """
    分块读取文件，计算 SHA-256 哈希值。
    """
    digest = hashlib.sha256()
    with file_path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_sensitivity(file_name: str, relative_path: str) -> str:
    """
    根据文件名和路径判断敏感等级。
    返回 LOW / MEDIUM / HIGH。
    """
    target = f"{file_name} {relative_path}".lower()
    if any(keyword.lower() in target for keyword in SENSITIVE_KEYWORDS):
        return "HIGH"
    if any(keyword.lower() in target for keyword in MEDIUM_KEYWORDS):
        return "MEDIUM"
    return "LOW"


def _should_skip(path: Path) -> bool:
    """Return True for hidden files, temp files, and cache artifacts."""
    names = path.parts
    if any(name.startswith(".") for name in names):
        return True
    lower_name = path.name.lower()
    return (
        lower_name.startswith("~")
        or lower_name.endswith(".tmp")
        or lower_name.endswith(".swp")
        or lower_name.endswith(".bak")
        or lower_name == "thumbs.db"
    )


def scan_directory(root_dir: Path) -> dict[str, FileSnapshot]:
    """
    递归扫描指定目录，返回文件快照字典。
    key 为相对路径，value 为 FileSnapshot。
    """
    root_dir = root_dir.resolve(strict=False)
    ensure_inside_demo_workspace(root_dir)
    protected_root = PROTECTED_DIR.resolve(strict=False)
    try:
        root_dir.relative_to(protected_root)
    except ValueError as exc:
        raise ValueError("scan_directory only scans demo_workspace/protected_files") from exc

    snapshots: dict[str, FileSnapshot] = {}
    if not root_dir.exists():
        return snapshots

    for file_path in sorted(root_dir.rglob("*")):
        if not file_path.is_file():
            continue
        relative_path_obj = file_path.relative_to(root_dir)
        if _should_skip(relative_path_obj):
            continue
        relative_path = relative_path_obj.as_posix()
        stat = file_path.stat()
        snapshots[relative_path] = FileSnapshot(
            relative_path=relative_path,
            absolute_path=str(file_path.resolve()),
            file_name=file_path.name,
            extension=file_path.suffix.lower(),
            size=stat.st_size,
            mtime=stat.st_mtime,
            sha256=calculate_sha256(file_path),
            sensitivity=detect_sensitivity(file_path.name, relative_path),
        )
    return snapshots

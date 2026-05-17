"""Demo workspace creation and safe risk simulation helpers."""

from __future__ import annotations

import shutil
from pathlib import Path

from .config import PROTECTED_DIR
from .utils import ensure_dir, ensure_inside_demo_workspace


DEMO_FILES = {
    "finance_report.txt": "模拟财务报告：本文件仅用于课程演示，不包含真实财务数据。\n",
    "account_list.txt": "模拟账号清单：user_a, user_b；不包含真实密码或真实账号。\n",
    "contract_2025.txt": "模拟合同文件：课程演示用合同摘要，无真实业务约束。\n",
    "project_plan.txt": "模拟项目计划：用于展示中敏感资料的哈希基线。\n",
    "normal_note.txt": "普通笔记：记录系统演示步骤和观察结果。\n",
}


def _protected_target(base_dir: Path) -> Path:
    """Return protected_files directory for a demo base path."""
    return base_dir if base_dir.name == "protected_files" else base_dir / "protected_files"


def create_demo_workspace(base_dir: Path) -> Path:
    """
    创建演示工作区和模拟敏感文件。
    """
    target = _protected_target(base_dir)
    ensure_inside_demo_workspace(target)
    ensure_dir(target)
    for file_name, content in DEMO_FILES.items():
        (target / file_name).write_text(content, encoding="utf-8")
    return target


def simulate_modify(root_dir: Path) -> None:
    """
    模拟篡改 finance_report.txt。
    """
    root_dir = ensure_inside_demo_workspace(root_dir)
    target = root_dir / "finance_report.txt"
    target.write_text(
        "模拟财务报告：内容已被篡改，用于触发哈希变化检测。\n",
        encoding="utf-8",
    )


def simulate_delete(root_dir: Path) -> None:
    """
    模拟删除 account_list.txt。
    """
    root_dir = ensure_inside_demo_workspace(root_dir)
    target = root_dir / "account_list.txt"
    if target.exists():
        target.unlink()


def simulate_bulk_change(root_dir: Path) -> None:
    """
    模拟批量修改多个文件。
    """
    root_dir = ensure_inside_demo_workspace(root_dir)
    changes = {
        "finance_report.txt": "模拟财务报告：批量异常变化版本。\n",
        "contract_2025.txt": "模拟合同文件：批量异常变化版本。\n",
        "project_plan.txt": "模拟项目计划：批量异常变化版本。\n",
    }
    for file_name, content in changes.items():
        (root_dir / file_name).write_text(content, encoding="utf-8")


def simulate_suspicious_file(root_dir: Path) -> None:
    """
    模拟新增 suspicious.ps1。
    注意：只写入无害文本，不执行。
    """
    root_dir = ensure_inside_demo_workspace(root_dir)
    (root_dir / "suspicious.ps1").write_text(
        "# harmless demo text only; this file is never executed.\n",
        encoding="utf-8",
    )


def reset_demo_workspace(base_dir: Path) -> Path:
    """
    重置演示目录，方便重复演示。
    """
    target = _protected_target(base_dir)
    ensure_inside_demo_workspace(target)
    if target.exists():
        shutil.rmtree(target)
    ensure_dir(PROTECTED_DIR.parent)
    return create_demo_workspace(base_dir)

import shutil

import pytest

from file_guard.backup import backup_files, restore_file, verify_restored_file
from file_guard.baseline import init_database, save_baseline
from file_guard.config import DATA_DIR, DEMO_WORKSPACE_DIR, PROTECTED_DIR
from file_guard.demo import reset_demo_workspace
from file_guard.scanner import scan_directory


def test_backup_restore_and_verify(tmp_path):
    root = reset_demo_workspace(DEMO_WORKSPACE_DIR)
    snapshots = scan_directory(PROTECTED_DIR)
    db_path = tmp_path / "file_guard.db"
    backup_dir = DATA_DIR / "test_backups"
    if backup_dir.exists():
        shutil.rmtree(backup_dir)

    init_database(db_path)
    save_baseline(db_path, snapshots)
    backup_files(root, backup_dir, snapshots, db_path)

    target = root / "account_list.txt"
    target.unlink()
    assert restore_file(root, backup_dir, "account_list.txt") is True

    verified, message = verify_restored_file(root, snapshots, "account_list.txt")
    assert verified is True
    assert "passed" in message


def test_restore_forbids_path_traversal():
    root = reset_demo_workspace(DEMO_WORKSPACE_DIR)
    with pytest.raises(ValueError):
        restore_file(root, DATA_DIR / "test_backups", "../outside.txt")

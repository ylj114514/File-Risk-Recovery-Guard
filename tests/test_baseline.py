from file_guard.baseline import get_baseline_count, init_database, load_baseline, save_baseline
from file_guard.config import DEMO_WORKSPACE_DIR, PROTECTED_DIR
from file_guard.demo import reset_demo_workspace
from file_guard.scanner import scan_directory


def test_init_database_save_and_load_baseline(tmp_path):
    db_path = tmp_path / "file_guard.db"
    reset_demo_workspace(DEMO_WORKSPACE_DIR)
    snapshots = scan_directory(PROTECTED_DIR)

    init_database(db_path)
    save_baseline(db_path, snapshots)
    loaded = load_baseline(db_path)

    assert db_path.exists()
    assert get_baseline_count(db_path) == len(snapshots)
    assert loaded.keys() == snapshots.keys()
    assert loaded["account_list.txt"].sha256 == snapshots["account_list.txt"].sha256

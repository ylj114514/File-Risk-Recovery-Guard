from file_guard.config import DEMO_WORKSPACE_DIR, PROTECTED_DIR
from file_guard.demo import reset_demo_workspace
from file_guard.models import FileSnapshot
from file_guard.scanner import calculate_sha256, detect_sensitivity, scan_directory


def test_calculate_sha256():
    root = reset_demo_workspace(DEMO_WORKSPACE_DIR)
    target = root / "hash_test.txt"
    target.write_text("abc", encoding="utf-8")

    assert calculate_sha256(target) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_detect_sensitivity_high():
    assert detect_sensitivity("account_list.txt", "account_list.txt") == "HIGH"


def test_detect_sensitivity_medium():
    assert detect_sensitivity("project_plan.txt", "project_plan.txt") == "MEDIUM"


def test_detect_sensitivity_low():
    assert detect_sensitivity("readme.txt", "readme.txt") == "LOW"


def test_scan_directory_returns_filesnapshot():
    reset_demo_workspace(DEMO_WORKSPACE_DIR)
    snapshots = scan_directory(PROTECTED_DIR)

    assert "finance_report.txt" in snapshots
    assert isinstance(snapshots["finance_report.txt"], FileSnapshot)
    assert snapshots["finance_report.txt"].sha256
    assert snapshots["finance_report.txt"].sensitivity == "HIGH"

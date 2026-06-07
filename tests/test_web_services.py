from file_guard.web import services


def test_get_system_status_returns_dict():
    status = services.get_system_status()
    assert isinstance(status, dict)
    assert "protected_file_count" in status


def test_get_baseline_files_returns_list():
    assert isinstance(services.get_baseline_files(), list)


def test_get_risk_events_returns_list():
    assert isinstance(services.get_risk_events(), list)


def test_service_demo_flow():
    reset_result = services.run_reset()
    assert reset_result["success"] is True

    demo_result = services.run_demo_init()
    assert demo_result["success"] is True

    baseline_result = services.run_baseline_init()
    assert baseline_result["success"] is True
    assert baseline_result["data"]["scanned_files"] >= 5

    simulation_result = services.run_simulation("delete")
    assert simulation_result["success"] is True

    scan_result = services.run_scan()
    assert scan_result["success"] is True
    assert scan_result["data"]["event_count"] >= 1

    recover_result = services.run_simulation_recover()
    assert recover_result["success"] is True
    assert recover_result["data"]["cleared_events"] is True

    invalid_restore = services.run_restore("../outside.txt")
    assert invalid_restore["success"] is False

    restore_result = services.run_restore("account_list.txt")
    assert restore_result["success"] is True

    report_result = services.run_report_export()
    assert report_result["success"] is True
    assert report_result["data"]["html"].endswith("report.html")

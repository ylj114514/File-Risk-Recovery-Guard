"""Flask page and API routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request, send_file

from ..config import OUTPUT_DIR
from . import services


bp = Blueprint("file_guard", __name__)


def _ok(message: str, data: object | None = None):
    """Return a successful JSON response."""
    return jsonify({"success": True, "message": message, "data": data or {}})


def _fail(message: str, status: int = 400):
    """Return a failed JSON response."""
    return jsonify({"success": False, "message": message, "data": None}), status


def _service_response(result: dict):
    """Convert service response dictionaries to Flask responses."""
    status = 200 if result.get("success") else 400
    return jsonify(result), status


@bp.get("/")
def dashboard():
    """Render dashboard page."""
    return render_template("dashboard.html", title="仪表盘")


@bp.get("/baseline")
def baseline_page():
    """Render baseline page."""
    return render_template("baseline.html", title="基线文件")


@bp.get("/events")
def events_page():
    """Render risk events page."""
    return render_template("events.html", title="风险事件")


@bp.get("/scan")
def scan_page():
    """Render scan page."""
    return render_template("scan.html", title="扫描检测")


@bp.get("/simulate")
def simulate_page():
    """Render simulation page."""
    return render_template("simulate.html", title="模拟风险")


@bp.get("/restore")
def restore_page():
    """Render restore page."""
    return render_template("restore.html", title="文件恢复")


@bp.get("/reports")
def reports_page():
    """Render reports page."""
    return render_template("reports.html", title="报告导出")


@bp.get("/reports/html")
def html_report_page():
    """Open generated HTML report."""
    report_path = OUTPUT_DIR / "report.html"
    if not report_path.exists():
        return _fail("HTML 报告尚未生成。", 404)
    return send_file(report_path)


@bp.get("/api/status")
def api_status():
    """Return system status."""
    return _ok("操作成功", services.get_system_status())


@bp.post("/api/demo-init")
def api_demo_init():
    """Create demo workspace."""
    return _service_response(services.run_demo_init())


@bp.post("/api/baseline/init")
def api_baseline_init():
    """Initialize baseline."""
    return _service_response(services.run_baseline_init())


@bp.post("/api/scan")
def api_scan():
    """Run risk scan."""
    return _service_response(services.run_scan())


@bp.post("/api/simulate")
def api_simulate():
    """Run safe simulation."""
    payload = request.get_json(silent=True) or {}
    case = payload.get("case") or request.form.get("case")
    if not case:
        return _fail("缺少模拟类型 case。")
    return _service_response(services.run_simulation(str(case)))


@bp.post("/api/simulation/recover")
def api_simulation_recover():
    """Recover the demo workspace from simulated changes."""
    return _service_response(services.run_simulation_recover())


@bp.post("/api/restore")
def api_restore():
    """Restore a file from backup."""
    payload = request.get_json(silent=True) or {}
    relative_path = payload.get("path") or request.form.get("path")
    if not relative_path:
        return _fail("缺少文件相对路径 path。")
    return _service_response(services.run_restore(str(relative_path)))


@bp.post("/api/report")
def api_report():
    """Generate reports."""
    return _service_response(services.run_report_export())


@bp.post("/api/reset")
def api_reset():
    """Reset demo environment."""
    return _service_response(services.run_reset())


@bp.get("/api/baseline")
def api_baseline():
    """Return baseline file list."""
    return _ok("操作成功", {"files": services.get_baseline_files()})


@bp.get("/api/events")
def api_events():
    """Return risk events."""
    return _ok("操作成功", {"events": services.get_risk_events()})

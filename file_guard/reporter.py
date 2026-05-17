"""Risk event persistence and report export functions."""

from __future__ import annotations

import csv
import html
import json
import sqlite3
from pathlib import Path

from .baseline import init_database
from .models import RiskEvent
from .risk_engine import explain_impact
from .utils import ensure_dir, now_text


def save_events_to_db(db_path: Path, events: list[RiskEvent]) -> None:
    """
    将风险事件保存到数据库。
    """
    init_database(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            """
            INSERT INTO risk_events (
                event_type, relative_path, old_hash, new_hash, old_size,
                new_size, score, level, evidence, suggestion, detected_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    event.event_type,
                    event.relative_path,
                    event.old_hash,
                    event.new_hash,
                    event.old_size,
                    event.new_size,
                    event.score,
                    event.level,
                    event.evidence,
                    event.suggestion,
                    event.detected_at,
                )
                for event in events
            ],
        )
        conn.commit()


def load_events_from_db(db_path: Path) -> list[RiskEvent]:
    """
    从数据库读取风险事件。
    """
    if not db_path.exists():
        return []
    init_database(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT event_type, relative_path, old_hash, new_hash, old_size,
                   new_size, score, level, evidence, suggestion, detected_at
            FROM risk_events
            ORDER BY id DESC
            """
        ).fetchall()
    return [
        RiskEvent(
            event_type=row["event_type"],
            relative_path=row["relative_path"],
            old_hash=row["old_hash"],
            new_hash=row["new_hash"],
            old_size=row["old_size"],
            new_size=row["new_size"],
            score=int(row["score"]),
            level=row["level"],
            evidence=row["evidence"],
            suggestion=row["suggestion"],
            detected_at=row["detected_at"],
        )
        for row in rows
    ]


def clear_events(db_path: Path) -> None:
    """
    清空历史风险事件。
    """
    init_database(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM risk_events")
        conn.commit()


def export_events_json(events: list[RiskEvent], output_path: Path) -> None:
    """
    导出 JSON 风险事件文件。
    """
    ensure_dir(output_path.parent)
    output_path.write_text(
        json.dumps([event.to_dict() for event in events], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def export_events_csv(events: list[RiskEvent], output_path: Path) -> None:
    """
    导出 CSV 风险事件文件。
    """
    ensure_dir(output_path.parent)
    with output_path.open("w", encoding="utf-8-sig", newline="") as file_obj:
        writer = csv.DictWriter(
            file_obj,
            fieldnames=[
                "event_type", "relative_path", "old_hash", "new_hash",
                "old_size", "new_size", "score", "level", "evidence",
                "suggestion", "detected_at",
            ],
        )
        writer.writeheader()
        for event in events:
            writer.writerow(event.to_dict())


def _level_counts(events: list[RiskEvent]) -> dict[str, int]:
    counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for event in events:
        counts[event.level] = counts.get(event.level, 0) + 1
    return counts


def generate_html_report(
    events: list[RiskEvent],
    output_path: Path,
    root_dir: Path
) -> None:
    """
    生成 HTML 风险报告。
    """
    ensure_dir(output_path.parent)
    counts = _level_counts(events)
    rows = []
    for event in events:
        impact = explain_impact(event.event_type, event.relative_path, event.level)
        rows.append(
            "<tr>"
            f"<td><span class='badge {html.escape(event.level.lower())}'>{html.escape(event.level)}</span></td>"
            f"<td>{event.score}</td>"
            f"<td>{html.escape(event.event_type)}</td>"
            f"<td>{html.escape(event.relative_path)}</td>"
            f"<td>{html.escape(event.evidence)}</td>"
            f"<td>{html.escape(impact)}</td>"
            f"<td>{html.escape(event.suggestion)}</td>"
            f"<td>{html.escape(event.detected_at)}</td>"
            "</tr>"
        )
    if not rows:
        rows.append("<tr><td colspan='8' class='empty'>暂无风险事件</td></tr>")

    report_html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>File-Risk-Recovery-Guard 风险报告</title>
  <style>
    body {{ margin: 0; background: #f3f6fa; color: #172033; font-family: Arial, "Microsoft YaHei", sans-serif; }}
    .page {{ max-width: 1180px; margin: 0 auto; padding: 28px; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    .subtitle {{ color: #526070; margin-bottom: 22px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 18px 0; }}
    .card {{ background: #fff; border: 1px solid #dce3ee; border-radius: 8px; padding: 16px; }}
    .card strong {{ display: block; font-size: 24px; margin-top: 6px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #dce3ee; }}
    th, td {{ border-bottom: 1px solid #e6ebf2; padding: 10px; vertical-align: top; text-align: left; font-size: 13px; }}
    th {{ background: #eaf0f7; color: #243246; }}
    .badge {{ display: inline-block; min-width: 72px; padding: 4px 8px; border-radius: 999px; text-align: center; font-weight: 700; }}
    .low {{ background: #dff5e7; color: #17623a; }}
    .medium {{ background: #fff2bd; color: #815800; }}
    .high {{ background: #ffe2c2; color: #a24b00; }}
    .critical {{ background: #ffd4d8; color: #a80f22; }}
    .empty {{ text-align: center; color: #6b7788; }}
  </style>
</head>
<body>
  <main class="page">
    <h1>基于文件哈希基线的敏感文件异常删除、篡改检测与恢复验证系统</h1>
    <div class="subtitle">报告生成时间：{html.escape(now_text())}；受保护目录：{html.escape(str(root_dir))}</div>
    <section class="grid">
      <div class="card">风险事件总数<strong>{len(events)}</strong></div>
      <div class="card">HIGH 风险事件<strong>{counts.get("HIGH", 0)}</strong></div>
      <div class="card">CRITICAL 风险事件<strong>{counts.get("CRITICAL", 0)}</strong></div>
      <div class="card">风险等级分布<strong>LOW {counts.get("LOW", 0)} / MEDIUM {counts.get("MEDIUM", 0)} / HIGH {counts.get("HIGH", 0)} / CRITICAL {counts.get("CRITICAL", 0)}</strong></div>
    </section>
    <h2>风险事件明细</h2>
    <table>
      <thead>
        <tr>
          <th>风险等级</th>
          <th>风险分值</th>
          <th>触发条件</th>
          <th>风险对象</th>
          <th>风险证据</th>
          <th>影响分析</th>
          <th>防护建议</th>
          <th>检测时间</th>
        </tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </main>
</body>
</html>
"""
    output_path.write_text(report_html, encoding="utf-8")

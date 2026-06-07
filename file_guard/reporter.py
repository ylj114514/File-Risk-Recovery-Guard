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
    """将风险事件保存到数据库。"""
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
    """从数据库读取风险事件。"""
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
    """清空历史风险事件。"""
    init_database(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM risk_events")
        conn.commit()


def export_events_json(events: list[RiskEvent], output_path: Path) -> None:
    """导出 JSON 风险事件文件。"""
    ensure_dir(output_path.parent)
    output_path.write_text(
        json.dumps([event.to_dict() for event in events], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def export_events_csv(events: list[RiskEvent], output_path: Path) -> None:
    """导出 CSV 风险事件文件。"""
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
    """Count events by level."""
    counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for event in events:
        counts[event.level] = counts.get(event.level, 0) + 1
    return counts


def _parse_evidence(evidence: str) -> dict[str, str]:
    """Parse the semicolon-separated evidence string into display fields."""
    fields: dict[str, str] = {}
    for part in evidence.split(";"):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def _field(label: str, value: object) -> str:
    safe_value = "-" if value is None or value == "" else str(value)
    return (
        "<div class='field'>"
        f"<span>{html.escape(label)}</span>"
        f"<strong>{html.escape(safe_value)}</strong>"
        "</div>"
    )


def _rules_list(rules_text: str) -> str:
    rules = [rule.strip() for rule in rules_text.split("|") if rule.strip()]
    if not rules:
        return "<strong>-</strong>"
    return "<ul>" + "".join(f"<li>{html.escape(rule)}</li>" for rule in rules) + "</ul>"


def _event_card(event: RiskEvent) -> str:
    fields = _parse_evidence(event.evidence)
    impact = explain_impact(event.event_type, event.relative_path, event.level)
    evidence_fields = [
        ("事件类型", fields.get("事件类型", event.event_type)),
        ("文件路径", fields.get("文件路径", event.relative_path)),
        ("旧哈希", fields.get("old_hash", event.old_hash or "-")),
        ("新哈希", fields.get("new_hash", event.new_hash or "-")),
        ("哈希是否变化", fields.get("hash_changed", "-")),
        ("旧文件大小", fields.get("old_size", event.old_size)),
        ("新文件大小", fields.get("new_size", event.new_size)),
        ("大小是否变化", fields.get("size_changed", "-")),
        ("敏感关键词", fields.get("敏感关键词", "-")),
        ("文件敏感等级", fields.get("文件敏感等级", "-")),
    ]
    evidence_html = "".join(_field(label, value) for label, value in evidence_fields)
    rules_html = _rules_list(fields.get("命中风险规则", ""))
    return f"""
    <article class="event-card {html.escape(event.level.lower())}">
      <header class="event-head">
        <div>
          <span class="badge {html.escape(event.level.lower())}">{html.escape(event.level)}</span>
          <h3>{html.escape(event.event_type)}：{html.escape(event.relative_path)}</h3>
        </div>
        <div class="score-box"><span>风险分值</span><strong>{event.score}</strong></div>
      </header>
      <section class="field-stack">
        {_field("检测时间", event.detected_at)}
        {_field("风险对象", event.relative_path)}
        {_field("触发条件", event.event_type)}
        {_field("影响分析", impact)}
        {_field("防护建议", event.suggestion)}
      </section>
      <section class="evidence-card">
        <h4>证据摘要</h4>
        <div class="field-stack">{evidence_html}</div>
        <div class="rules">
          <span>命中风险规则</span>
          {rules_html}
        </div>
      </section>
    </article>
    """


def generate_html_report(
    events: list[RiskEvent],
    output_path: Path,
    root_dir: Path
) -> None:
    """生成 HTML 风险报告。"""
    ensure_dir(output_path.parent)
    counts = _level_counts(events)
    event_cards = "".join(_event_card(event) for event in events)
    if not event_cards:
        event_cards = "<div class='empty'>暂无风险事件。当前目录与基线一致。</div>"

    report_html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>File-Risk-Recovery-Guard 风险报告</title>
  <style>
    :root {{
      --bg: #f3f6fa;
      --surface: #ffffff;
      --border: #d7e0eb;
      --text: #172033;
      --muted: #526070;
      --blue: #1f6fbf;
      --green: #17623a;
      --gold: #815800;
      --orange: #a24b00;
      --red: #a80f22;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Arial, "Microsoft YaHei", "PingFang SC", sans-serif;
      line-height: 1.65;
    }}
    .page {{ max-width: 1180px; margin: 0 auto; padding: 30px; }}
    .hero, .summary-card, .event-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      box-shadow: 0 14px 34px rgba(31, 48, 74, 0.08);
    }}
    .hero {{ padding: 24px; margin-bottom: 18px; }}
    .eyebrow {{ color: var(--blue); font-size: 12px; font-weight: 800; text-transform: uppercase; }}
    h1 {{ margin: 8px 0; font-size: 28px; line-height: 1.35; }}
    h2 {{ margin: 24px 0 12px; font-size: 22px; }}
    h3 {{ margin: 0; font-size: 18px; }}
    h4 {{ margin: 0 0 10px; font-size: 16px; }}
    .subtitle {{ color: var(--muted); margin: 0; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 18px 0; }}
    .summary-card {{ padding: 16px; border-top: 5px solid #93a4b8; }}
    .summary-card span {{ display: block; color: var(--muted); }}
    .summary-card strong {{ display: block; margin-top: 6px; font-size: 26px; }}
    .event-list {{ display: grid; gap: 18px; }}
    .event-card {{ padding: 18px; border-left: 7px solid #93a4b8; }}
    .event-card.low {{ border-left-color: #35a66d; }}
    .event-card.medium {{ border-left-color: #d5a100; }}
    .event-card.high {{ border-left-color: #f07b16; }}
    .event-card.critical {{ border-left-color: #d7263d; }}
    .event-head {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 14px; padding-bottom: 14px; border-bottom: 1px solid #e6edf5; }}
    .event-head > div:first-child {{ display: flex; align-items: center; gap: 10px; min-width: 0; }}
    .score-box {{ min-width: 96px; padding: 8px 10px; border: 1px solid #dbe5f0; border-radius: 8px; background: #f8fbff; text-align: center; }}
    .score-box span {{ display: block; color: var(--muted); font-size: 12px; font-weight: 800; }}
    .score-box strong {{ display: block; color: var(--text); font-size: 26px; line-height: 1; margin-top: 3px; }}
    .badge {{ display: inline-block; min-width: 86px; padding: 5px 10px; border-radius: 999px; text-align: center; font-size: 12px; font-weight: 800; }}
    .badge.low {{ background: #dff3e8; color: var(--green); }}
    .badge.medium {{ background: #fff0b8; color: var(--gold); }}
    .badge.high {{ background: #ffe0bc; color: var(--orange); }}
    .badge.critical {{ background: #ffd2d7; color: var(--red); }}
    .field-stack {{ display: grid; gap: 8px; margin-top: 14px; }}
    .field {{ display: grid; grid-template-columns: 140px minmax(0, 1fr); gap: 12px; padding: 10px 12px; border: 1px solid #e4ebf3; border-radius: 8px; background: #f8fbff; }}
    .field span, .rules span {{ color: var(--muted); font-size: 12px; font-weight: 800; }}
    .field strong {{ color: var(--text); font-weight: 650; overflow-wrap: anywhere; word-break: break-word; }}
    .evidence-card {{ margin-top: 14px; padding: 14px; border: 1px solid #cfdeee; border-radius: 8px; background: #ffffff; }}
    .rules {{ display: grid; gap: 8px; margin-top: 10px; padding: 10px 12px; border: 1px solid #e4ebf3; border-radius: 8px; background: #fffdf5; }}
    .rules ul {{ margin: 0; padding-left: 20px; display: grid; gap: 6px; }}
    .empty {{ padding: 24px; color: var(--muted); text-align: center; background: #fff; border: 1px solid var(--border); border-radius: 8px; }}
    @media (max-width: 860px) {{
      .summary-grid {{ grid-template-columns: 1fr; }}
      .event-head, .field {{ grid-template-columns: 1fr; display: grid; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="eyebrow">File-Risk-Recovery-Guard</div>
      <h1>基于文件哈希基线的敏感文件异常删除、篡改检测与恢复验证系统</h1>
      <p class="subtitle">报告生成时间：{html.escape(now_text())}；受保护目录：{html.escape(str(root_dir))}</p>
    </section>
    <section class="summary-grid">
      <div class="summary-card"><span>风险事件总数</span><strong>{len(events)}</strong></div>
      <div class="summary-card"><span>HIGH 风险事件</span><strong>{counts.get("HIGH", 0)}</strong></div>
      <div class="summary-card"><span>CRITICAL 风险事件</span><strong>{counts.get("CRITICAL", 0)}</strong></div>
      <div class="summary-card"><span>等级分布</span><strong>LOW {counts.get("LOW", 0)} / MEDIUM {counts.get("MEDIUM", 0)} / HIGH {counts.get("HIGH", 0)} / CRITICAL {counts.get("CRITICAL", 0)}</strong></div>
    </section>
    <h2>风险事件明细</h2>
    <section class="event-list">{event_cards}</section>
  </main>
</body>
</html>
"""
    output_path.write_text(report_html, encoding="utf-8")

"""Risk scoring, level classification, and evidence generation."""

from __future__ import annotations

from .config import SENSITIVE_KEYWORDS, SUSPICIOUS_EXTENSIONS
from .models import RiskEvent
from .utils import now_text


def _matched_sensitive_keywords(text: str) -> list[str]:
    """Return high sensitivity keywords found in a path-like text."""
    lower_text = text.lower()
    return [keyword for keyword in SENSITIVE_KEYWORDS if keyword.lower() in lower_text]


def calculate_risk_score(change: dict, is_bulk: bool = False) -> tuple[int, list[str]]:
    """
    根据变更事件计算风险分值。
    返回风险分数和命中的风险规则说明列表。
    """
    score = 0
    rules: list[str] = []
    event_type = change.get("event_type", "")
    relative_path = change.get("relative_path", "")
    sensitivity = change.get("sensitivity", "LOW")
    extension = str(change.get("extension", "")).lower()
    new_size = change.get("new_size")
    change_count = int(change.get("change_count") or 0)

    # Core event weights make destructive or suspicious actions stand out.
    if event_type == "DELETED":
        score += 50
        rules.append("DELETED +50")
    elif event_type == "MODIFIED":
        score += 35
        rules.append("MODIFIED +35")
    elif event_type == "CREATED":
        score += 15
        rules.append("CREATED +15")
    elif event_type == "SUSPICIOUS_EXTENSION":
        score += 45
        rules.append("SUSPICIOUS_EXTENSION +45")
    elif event_type == "HIGH_SENSITIVE_CHANGED":
        score += 25
        rules.append("HIGH_SENSITIVE_CHANGED +25")
    elif event_type == "BULK_CHANGE":
        score += 25
        rules.append("BULK_CHANGE +25")

    matched = _matched_sensitive_keywords(relative_path)
    if matched:
        score += 20
        rules.append(f"sensitive keyword matched ({', '.join(matched)}) +20")

    if sensitivity == "HIGH":
        score += 25
        rules.append("HIGH sensitivity +25")
    elif sensitivity == "MEDIUM":
        score += 10
        rules.append("MEDIUM sensitivity +10")

    if extension in SUSPICIOUS_EXTENSIONS:
        score += 30
        rules.append(f"suspicious extension {extension} +30")

    if new_size == 0:
        score += 25
        rules.append("file size became 0 +25")

    if is_bulk or change_count >= 3:
        score += 25
        rules.append("bulk change count >= 3 +25")

    if event_type == "DELETED" and sensitivity == "HIGH":
        score += 20
        rules.append("deleted HIGH sensitivity file extra +20")
    if event_type == "MODIFIED" and sensitivity == "HIGH":
        score += 15
        rules.append("modified HIGH sensitivity file extra +15")

    return min(score, 100), rules


def classify_risk_level(score: int) -> str:
    """
    根据风险分值判断风险等级。
    """
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def generate_suggestion(event_type: str, level: str, relative_path: str) -> str:
    """
    根据事件类型、风险等级和文件路径生成防护建议。
    """
    base = "限制写入权限，保留最小权限访问，定期维护哈希基线与离线备份。"
    if event_type == "DELETED":
        action = "立即从备份恢复文件，核查删除来源，检查是否存在误操作或异常进程。"
    elif event_type == "MODIFIED":
        action = "从可信备份恢复或人工复核内容，确认修改来源，必要时冻结写权限。"
    elif event_type == "CREATED":
        action = "核查新增文件来源，确认是否为授权业务文件，必要时隔离后再分析。"
    elif event_type == "SUSPICIOUS_EXTENSION":
        action = "不要执行该文件，检查内容是否无害，删除未授权脚本并限制脚本写入。"
    elif event_type == "HIGH_SENSITIVE_CHANGED":
        action = "优先复核高敏感文件，恢复可信版本，并追踪账号、权限和操作时间。"
    elif event_type == "BULK_CHANGE":
        action = "立即停止批量写入来源，导出事件报告，逐项恢复并复核关键文件。"
    else:
        action = "复核文件变化来源并保留证据。"
    if level in {"HIGH", "CRITICAL"}:
        return f"{action} {base} 重点对象：{relative_path}"
    return f"{action} {base}"


def explain_impact(event_type: str, relative_path: str, level: str) -> str:
    """
    生成风险影响说明，用于报告展示。
    """
    if event_type == "DELETED":
        return f"{relative_path} 被删除可能导致业务资料不可用，若无可信备份会影响审计和恢复。"
    if event_type == "MODIFIED":
        return f"{relative_path} 内容哈希变化，可能造成敏感数据被篡改、污染或误用。"
    if event_type == "CREATED":
        return f"{relative_path} 为基线外新增文件，可能扩大敏感目录暴露面。"
    if event_type == "SUSPICIOUS_EXTENSION":
        return f"{relative_path} 使用可疑脚本或可执行扩展名，虽未执行，也需要防止被误触发。"
    if event_type == "HIGH_SENSITIVE_CHANGED":
        return f"{relative_path} 属于高敏感对象变化，可能涉及账号、财务、合同或客户资料风险。"
    if event_type == "BULK_CHANGE":
        return f"{relative_path} 出现批量异常变化，风险等级为 {level}，需要优先排查批量操作来源。"
    return f"{relative_path} 出现异常变化，风险等级为 {level}。"


def build_risk_event(change: dict, is_bulk: bool = False) -> RiskEvent:
    """
    将原始变更事件转换为完整 RiskEvent。
    """
    score, rules = calculate_risk_score(change, is_bulk=is_bulk)
    level = classify_risk_level(score)
    event_type = change.get("event_type", "UNKNOWN")
    relative_path = change.get("relative_path", "")
    old_hash = change.get("old_hash")
    new_hash = change.get("new_hash")
    old_size = change.get("old_size")
    new_size = change.get("new_size")
    keywords = _matched_sensitive_keywords(relative_path)
    hash_changed = old_hash != new_hash
    size_changed = old_size != new_size
    evidence = (
        f"事件类型: {event_type}; 文件路径: {relative_path}; "
        f"old_hash: {old_hash or '-'}; new_hash: {new_hash or '-'}; "
        f"hash_changed: {hash_changed}; old_size: {old_size}; new_size: {new_size}; "
        f"size_changed: {size_changed}; 敏感关键词: {', '.join(keywords) if keywords else '无'}; "
        f"文件敏感等级: {change.get('sensitivity', 'LOW')}; "
        f"命中风险规则: {' | '.join(rules) if rules else '无'}"
    )
    return RiskEvent(
        event_type=event_type,
        relative_path=relative_path,
        old_hash=old_hash,
        new_hash=new_hash,
        old_size=old_size,
        new_size=new_size,
        score=score,
        level=level,
        evidence=evidence,
        suggestion=generate_suggestion(event_type, level, relative_path),
        detected_at=now_text(),
    )
